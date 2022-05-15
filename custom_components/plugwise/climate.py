"""Plugwise Climate component for Home Assistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,  # pw-beta homekit emulation
    PRESET_HOME,  # pw-beta homekit emulation
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    # pw-beta homekit emulation
    homekit_enabled = config_entry.options.get(CONF_HOMEKIT_EMULATION, False)

    async_add_entities(
        PlugwiseClimateEntity(coordinator, device_id, homekit_enabled)
        for device_id, device in coordinator.data.devices.items()
        if device["dev_class"] in MASTER_THERMOSTATS
    )


class PlugwiseClimateEntity(PlugwiseEntity, ClimateEntity):
    """Representation of an Plugwise thermostat."""

    _attr_temperature_unit = TEMP_CELSIUS

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
        self._attr_name = self.device["name"]

        # Determine preset modes
        self._attr_supported_features = SUPPORT_TARGET_TEMPERATURE
        self._attr_preset_modes = None
        if presets := self.device["preset_modes"]:
            self._attr_supported_features |= SUPPORT_PRESET_MODE
            self._attr_preset_modes = presets

        self._attr_min_temp = self.device.get("lower_bound", DEFAULT_MIN_TEMP)
        self._attr_max_temp = self.device.get("upper_bound", DEFAULT_MAX_TEMP)
        if resolution := self.device.get("resolution", 0.1):
            # Ensure we don't drop below 0.1
            self._attr_target_temperature_step = max(resolution, 0.1)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.device["sensors"]["temperature"]

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.device["sensors"]["setpoint"]

    @property
    def hvac_mode(self) -> str:
        """Return HVAC operation ie. auto, heat, cool, or off mode."""
        if (mode := self.device["mode"]) is None or mode not in self.hvac_modes:
            return HVAC_MODE_HEAT
        # pw-beta homekit emulation
        if self._homekit_enabled and self._homekit_mode == HVAC_MODE_OFF:
            mode = HVAC_MODE_OFF
        return mode

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        # When control_state is present, prefer this data
        control_state: str = self.device.get("control_state", "not_found")
        if control_state == "cooling":
            return CURRENT_HVAC_COOL
        # Support preheating state as heating, until preheating is added as a separate state
        if control_state in ["heating", "preheating"]:
            return CURRENT_HVAC_HEAT
        if control_state == "off":
            return CURRENT_HVAC_IDLE

        heater_central_data = self.devices[self.gateway["heater_id"]]
        if heater_central_data["binary_sensors"]["heating_state"]:
            return CURRENT_HVAC_HEAT
        if heater_central_data["binary_sensors"].get("cooling_state", False):
            return CURRENT_HVAC_COOL

        return CURRENT_HVAC_IDLE

    @property
    def hvac_modes(self) -> list[str]:
        """Return the current hvac modes."""
        hvac_modes = [HVAC_MODE_HEAT]
        if self.gateway["cooling_present"]:
            if self.gateway["smile_name"] == "Anna":
                hvac_modes.append(HVAC_MODE_HEAT_COOL)
                hvac_modes.remove(HVAC_MODE_HEAT)
            if (
                self.gateway["smile_name"] == "Adam"
                and self.devices[self.gateway["gateway_id"]]["regulation_mode"]
                == "cooling"
            ):
                hvac_modes.append(HVAC_MODE_COOL)
                hvac_modes.remove(HVAC_MODE_HEAT)
        if self.device["available_schedules"] != ["None"]:
            hvac_modes.append(HVAC_MODE_AUTO)
        if self._homekit_enabled:  # pw-beta homekit emulation
            hvac_modes.append(HVAC_MODE_OFF)

        return hvac_modes

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        return self.device["active_preset"]

    @plugwise_command
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if ((temperature := kwargs.get(ATTR_TEMPERATURE)) is None) or (
            self._attr_max_temp < temperature < self._attr_min_temp
        ):
            raise ValueError("Invalid temperature requested")
        await self.coordinator.api.set_temperature(self.device["location"], temperature)

    @plugwise_command
    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set the hvac mode."""
        if hvac_mode not in self.hvac_modes:
            raise HomeAssistantError("Unsupported hvac_mode")

        if hvac_mode == HVAC_MODE_AUTO and self.device["last_used"] is None:
            raise HomeAssistantError(
                "Cannot set HVAC mode to Auto: no schedule available"
            )

        await self.coordinator.api.set_schedule_state(
            self.device["location"],
            self.device["last_used"],
            "on" if hvac_mode == HVAC_MODE_AUTO else "off",
        )

        # pw-beta: feature request - mimic HomeKit behavior
        self._homekit_mode = hvac_mode
        if self._homekit_enabled:
            if self._homekit_mode == HVAC_MODE_OFF:
                await self.async_set_preset_mode(PRESET_AWAY)
            if (
                self._homekit_mode
                in [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL]
                and self.device["active_preset"] == PRESET_AWAY
            ):
                await self.async_set_preset_mode(PRESET_HOME)

    @plugwise_command
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        if (
            self._attr_preset_modes is not None
            and preset_mode not in self._attr_preset_modes
        ):
            raise HomeAssistantError("Unsupported preset mode")

        await self.coordinator.api.set_preset(self.device["location"], preset_mode)
