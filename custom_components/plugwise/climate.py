"""Plugwise Climate component for Home Assistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,  # pw-beta homekit emulation
    PRESET_HOME,  # pw-beta homekit emulation
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    CONF_HOMEKIT_EMULATION,  # pw-beta homekit emulation
    COORDINATOR,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
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
        if device["class"] in MASTER_THERMOSTATS
    )


class PlugwiseClimateEntity(PlugwiseEntity, ClimateEntity):
    """Representation of an Plugwise thermostat."""

    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        enabled: bool,  # pw-beta homekit emulation
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)
        self._homekit_enabled = enabled  # pw-beta homekit emulation
        self._homekit_mode: str | None = None  # pw-beta homekit emulation
        self._attr_extra_state_attributes = {}
        self._attr_unique_id = f"{device_id}-climate"
        self._attr_name = self.device.get("name")

        # Determine preset modes
        self._attr_supported_features = SUPPORT_TARGET_TEMPERATURE
        if presets := self.device.get("presets"):
            self._attr_supported_features |= SUPPORT_PRESET_MODE
            self._attr_preset_modes = list(presets)

        # Determine hvac modes and current hvac mode
        self._attr_hvac_modes = [HVAC_MODE_HEAT]
        if self.coordinator.data.gateway.get("cooling_present"):
            self._attr_hvac_modes.append(HVAC_MODE_COOL)
        if self.device.get("available_schedules") != ["None"]:
            self._attr_hvac_modes.append(HVAC_MODE_AUTO)
        if self._homekit_enabled:  # pw-beta homekit emulation
            self._attr_hvac_modes.append(HVAC_MODE_OFF)

        self._attr_min_temp = self.device.get("lower_bound", DEFAULT_MIN_TEMP)
        self._attr_max_temp = self.device.get("upper_bound", DEFAULT_MAX_TEMP)
        if resolution := self.device.get("resolution"):
            # Ensure we don't drop below 0.1
            self._attr_target_temperature_step = max(resolution, 0.1)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.device["sensors"].get("temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.device["sensors"].get("setpoint")

    @property
    def hvac_mode(self) -> str:
        """Return HVAC operation ie. auto, heat, cool, or off mode."""
        if (mode := self.device.get("mode")) is None or mode not in self.hvac_modes:
            return HVAC_MODE_HEAT
        # pw-beta homekit emulation
        if (
            self._homekit_enabled and self._homekit_mode == HVAC_MODE_OFF
        ):
            mode = HVAC_MODE_OFF
        return mode

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        # When control_state is present, prefer this data
        if "control_state" in self.device:
            if self.device.get("control_state") == "cooling":
                return CURRENT_HVAC_COOL
            # Support preheating state as heating, until preheating is added as a separate state
            if self.device.get("control_state") in ["heating", "preheating"]:
                return CURRENT_HVAC_HEAT
        else:
            heater_central_data = self.coordinator.data.devices[
                self.coordinator.data.gateway["heater_id"]
            ]
            if heater_central_data["binary_sensors"].get("heating_state"):
                return CURRENT_HVAC_HEAT
            if heater_central_data["binary_sensors"].get("cooling_state"):
                return CURRENT_HVAC_COOL
        return CURRENT_HVAC_IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self.device.get("active_preset")

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
        self._homekit_mode = hvac_mode  # pw-beta homekit emulation
        if hvac_mode == HVAC_MODE_AUTO and not self.device.get("schedule_temperature"):
            raise ValueError("Cannot set HVAC mode to Auto: No schedule available")

        await self.coordinator.api.set_schedule_state(
            self.device["location"],
            self.device.get("last_used"),
            "on" if hvac_mode == HVAC_MODE_AUTO else "off",
        )

        # pw-beta: feature request - mimic HomeKit behavior
        if self._homekit_enabled:
            if self._homekit_mode == HVAC_MODE_OFF:
                await self.async_set_preset_mode(PRESET_AWAY)
            if (
                self._homekit_mode in [HVAC_MODE_HEAT, HVAC_MODE_COOL]
                and self.device["active_preset"] == PRESET_AWAY
            ):
                await self.async_set_preset_mode(PRESET_HOME)

    @plugwise_command
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        await self.coordinator.api.set_preset(self.device["location"], preset_mode)
