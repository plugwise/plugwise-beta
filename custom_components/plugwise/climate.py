"""Plugwise Climate component for Home Assistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    PRESET_AWAY,  # pw-beta homekit emulation
    PRESET_HOME,  # pw-beta homekit emulation
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    CONF_HOMEKIT_EMULATION,  # pw-beta homekit emulation
    COORDINATOR,
    DOMAIN,
    MASTER_THERMOSTATS,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile Thermostats from a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    # pw-beta homekit emulation
    homekit_enabled: bool = config_entry.options.get(CONF_HOMEKIT_EMULATION, False)

    async_add_entities(
        PlugwiseClimateEntity(coordinator, device_id, homekit_enabled)
        for device_id, device in coordinator.data.devices.items()
        if device["dev_class"] in MASTER_THERMOSTATS
    )


class PlugwiseClimateEntity(PlugwiseEntity, ClimateEntity):
    """Representation of an Plugwise thermostat."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        homekit_enabled: bool,  # pw-beta homekit emulation
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)
        self._homekit_enabled = homekit_enabled  # pw-beta homekit emulation
        self._homekit_mode: str | None = None  # pw-beta homekit emulation
        self._attr_unique_id = f"{device_id}-climate"

        # Determine preset modes
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        if presets := self.device.get("preset_modes"):
            self._attr_supported_features |= ClimateEntityFeature.PRESET_MODE
            self._attr_preset_modes = presets

        # Determine hvac modes and current hvac mode
        self._attr_hvac_modes = [HVACMode.HEAT]
        if self.coordinator.data.gateway["cooling_present"]:
            self._attr_hvac_modes.append(HVACMode.COOL)
        if self.device["available_schedules"] != ["None"]:
            self._attr_hvac_modes.append(HVACMode.AUTO)

        self._attr_min_temp = self.device["thermostat"].get(
            "lower_bound", DEFAULT_MIN_TEMP
        )
        self._attr_max_temp = self.device["thermostat"].get(
            "upper_bound", DEFAULT_MAX_TEMP
        )
        if resolution := self.device["thermostat"]["resolution"]:
            # Ensure we don't drop below 0.1
            self._attr_target_temperature_step = max(resolution, 0.1)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.device["sensors"]["temperature"]

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation if supported."""
        # When control_state is present, prefer this data
        if (control_state := self.device.get("control_state")) == "cooling":
            return HVACAction.COOLING
        # Support preheating state as heating, until preheating is added as a separate state
        if control_state in ["heating", "preheating"]:
            return HVACAction.HEATING
        if control_state == "off":
            return HVACAction.IDLE

        hc_data = self.devices[self.gateway["heater_id"]]
        if hc_data["binary_sensors"]["heating_state"]:
            return HVACAction.HEATING
        if hc_data["binary_sensors"].get("cooling_state", False):
            return HVACAction.COOLING

        return HVACAction.IDLE

    @property
    def hvac_mode(self) -> HVACMode:
        """Return HVAC operation ie. auto, heat, cool, or off mode."""
        if (mode := self.device["mode"]) is None or mode not in self.hvac_modes:
            return HVACMode.HEAT  # pragma: no cover
        # pw-beta homekit emulation
        if self._homekit_enabled and self._homekit_mode == HVACMode.OFF:
            mode = HVACMode.OFF  # pragma: no cover

        return HVACMode(mode)

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        return self.device["active_preset"]

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""

        return self.device["thermostat"]["setpoint"]

    @plugwise_command
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if ATTR_HVAC_MODE in kwargs:
            await self.async_set_hvac_mode(kwargs[ATTR_HVAC_MODE])

        if ((temperature := kwargs.get(ATTR_TEMPERATURE)) is None) or not (
            self._attr_min_temp <= temperature <= self._attr_max_temp
        ):
            raise ValueError("Invalid temperature requested")

        await self.coordinator.api.set_temperature(self.device["location"], temperature)

    @plugwise_command
    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set the hvac mode."""
        if hvac_mode not in self.hvac_modes:
            raise HomeAssistantError("Unsupported hvac_mode")

        await self.coordinator.api.set_schedule_state(
            self.device["location"],
            self.device["last_used"],
            "on" if hvac_mode == HVACMode.AUTO else "off",
        )

        # pw-beta: feature request - mimic HomeKit behavior
        self._homekit_mode = hvac_mode
        if self._homekit_enabled:
            if self._homekit_mode == HVACMode.OFF:  # pragma: no cover
                await self.async_set_preset_mode(PRESET_AWAY)  # pragma: no cover
            if (
                self._homekit_mode in [HVACMode.HEAT, HVACMode.COOL, HVACMode.HEAT_COOL]
                and self.device["active_preset"] == PRESET_AWAY
            ):  # pragma: no cover
                await self.async_set_preset_mode(PRESET_HOME)  # pragma: no cover

    @plugwise_command
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        await self.coordinator.api.set_preset(self.device["location"], preset_mode)
