"""Plugwise Climate component for Home Assistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_AWAY,  # pw-beta homekit emulation
)
from homeassistant.components.climate.const import (
    PRESET_HOME,  # pw-beta homekit emulation
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOMEKIT_EMULATION  # pw-beta homekit emulation
from .const import COORDINATOR  # pw-beta
from .const import DOMAIN, MASTER_THERMOSTATS
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

    homekit_enabled: bool = config_entry.options.get(
        CONF_HOMEKIT_EMULATION, False
    )  # pw-beta homekit emulation

    async_add_entities(
        PlugwiseClimateEntity(
            coordinator, device_id, homekit_enabled
        )  # pw-beta homekit emulation
        for device_id, device in coordinator.data.devices.items()
        if device["dev_class"] in MASTER_THERMOSTATS
    )


class PlugwiseClimateEntity(PlugwiseEntity, ClimateEntity):
    """Representation of an Plugwise thermostat."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = DOMAIN

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

        # Determine supported features
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        if self.coordinator.data.gateway["cooling_present"]:
            self._attr_supported_features = (
                ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
            )
        if presets := self.device.get("preset_modes"):
            self._attr_supported_features |= ClimateEntityFeature.PRESET_MODE
            self._attr_preset_modes = presets

        # Determine hvac modes and current hvac mode
        self._attr_hvac_modes = [HVACMode.HEAT]
        if self.coordinator.data.gateway["cooling_present"]:
            self._attr_hvac_modes = [HVACMode.HEAT_COOL]
        if self.device["available_schedules"] != ["None"]:
            self._attr_hvac_modes.append(HVACMode.AUTO)
        if self._homekit_enabled:  # pw-beta homekit emulation
            self._attr_hvac_modes.append(HVACMode.OFF)  # pragma: no cover

        self._attr_min_temp = self.device["thermostat"]["lower_bound"]
        self._attr_max_temp = self.device["thermostat"]["upper_bound"]
        # Ensure we don't drop below 0.1
        self._attr_target_temperature_step = max(
            self.device["thermostat"]["resolution"], 0.1
        )

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.device["sensors"]["temperature"]

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach.

        Connected to the HVACMode combination of AUTO-HEAT.
        """

        return self.device["thermostat"]["setpoint"]

    @property
    def target_temperature_high(self) -> float:
        """Return the temperature we try to reach in case of cooling.

        Connected to the HVACMode combination of AUTO-HEAT_COOL.
        """
        return self.device["thermostat"]["setpoint_high"]

    @property
    def target_temperature_low(self) -> float:
        """Return the heating temperature we try to reach in case of heating.

        Connected to the HVACMode combination AUTO-HEAT_COOL.
        """
        return self.device["thermostat"]["setpoint_low"]

    @property
    def hvac_mode(self) -> HVACMode:
        """Return HVAC operation ie. auto, heat, heat_cool, or off mode."""
        if (
            mode := self.device["mode"]
        ) is None or mode not in self.hvac_modes:  # pw-beta add to Core
            return HVACMode.HEAT  # pragma: no cover
        # pw-beta homekit emulation
        if self._homekit_enabled and self._homekit_mode == HVACMode.OFF:
            mode = HVACMode.OFF  # pragma: no cover

        return HVACMode(mode)

    @property
    def hvac_action(self) -> HVACAction:  # pw-beta add to Core
        """Return the current running hvac operation if supported."""
        # When control_state is present, prefer this data
        if (control_state := self.device.get("control_state")) == "cooling":
            return HVACAction.COOLING
        # Support preheating state as heating,
        # until preheating is added as a separate state
        if control_state in ["heating", "preheating"]:
            return HVACAction.HEATING
        if control_state == "off":
            return HVACAction.IDLE

        heater: str | None = self.coordinator.data.gateway["heater_id"]
        if heater is not None:
            heater_data = self.coordinator.data.devices[heater]
            if heater_data["binary_sensors"]["heating_state"]:
                return HVACAction.HEATING
            if heater_data["binary_sensors"].get("cooling_state", False):
                return HVACAction.COOLING

        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self.device["active_preset"]

    @plugwise_command
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if ATTR_HVAC_MODE in kwargs:  # pw-beta add to Core
            await self.async_set_hvac_mode(
                kwargs[ATTR_HVAC_MODE]
            )  # pw-beta add to Core

        data: dict[str, Any] = {}
        if ATTR_TEMPERATURE in kwargs:
            data["setpoint"] = kwargs.get(ATTR_TEMPERATURE)
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            data["setpoint_high"] = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        if ATTR_TARGET_TEMP_LOW in kwargs:
            data["setpoint_low"] = kwargs.get(ATTR_TARGET_TEMP_LOW)

        for temperature in data.values():
            if temperature is None or not (
                self._attr_min_temp <= temperature <= self._attr_max_temp
            ):
                raise ValueError("Invalid temperature change requested")

        await self.coordinator.api.set_temperature(self.device["location"], data)

    @plugwise_command
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
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
