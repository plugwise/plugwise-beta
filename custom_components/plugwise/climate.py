"""Plugwise Climate component for Home Assistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
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
        self._hc_data = self.devices[self.gateway["heater_id"]]
        self._homekit_enabled = homekit_enabled  # pw-beta homekit emulation
        self._homekit_mode: str | None = None  # pw-beta homekit emulation
        self._attr_unique_id = f"{device_id}-climate"

        if presets := self.device.get("preset_modes"):
            self._attr_preset_modes = presets

        self._attr_min_temp = self.device["thermostat"].get(
            "lower_bound", DEFAULT_MIN_TEMP
        )
        self._attr_max_temp = self.device["thermostat"].get(
            "upper_bound", DEFAULT_MAX_TEMP
        )
        if resolution := self.device["thermostat"].get("resolution", 0.1):
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
        control_state: str = self.device.get("control_state", "not_found")
        if control_state == "cooling":
            return HVACAction.COOLING
        # Support preheating state as heating, until preheating is added as a separate state
        if control_state in ["heating", "preheating"]:
            return HVACAction.HEATING
        if control_state == "off":
            return HVACAction.IDLE

        if self._hc_data["binary_sensors"]["heating_state"]:
            return HVACAction.HEATING
        if self._hc_data["binary_sensors"].get("cooling_state", False):
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
    def hvac_modes(self) -> list[HVACMode]:
        """Return the current hvac modes."""
        hvac_modes = [HVACMode.HEAT]
        if self.gateway["cooling_present"]:
            if self._hc_data.get("elga_cooling_enabled", False):
                hvac_modes.append(HVACMode.HEAT_COOL)
                hvac_modes.remove(HVACMode.HEAT)
            if self._hc_data.get(
                "lortherm_cooling_enabled", False
            ) or self._hc_data.get("adam_cooling_enabled", False):
                hvac_modes.append(HVACMode.COOL)
                hvac_modes.remove(HVACMode.HEAT)
        if self.device["available_schedules"] != ["None"]:
            hvac_modes.append(HVACMode.AUTO)

        return hvac_modes

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        return self.device["active_preset"]

    @property
    def supported_features(self) -> int:
        """Return the supported features."""
        features: int = ClimateEntityFeature.TARGET_TEMPERATURE
        if self._hc_data.get("elga_cooling_enabled", False):
            features = ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        if self.device.get("preset_modes"):
            features |= ClimateEntityFeature.PRESET_MODE

        return features

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach.

        Connected to the HVACModes combinations of AUTO/HEAT and AUTO/COOL.
        """

        return self.device["thermostat"].get("setpoint")

    @property
    def target_temperature_high(self) -> float | None:
        """Return the temperature we try to reach in case of cooling.

        Connected to the HVACMode combination of AUTO/HEAT_COOL.
        """
        return self.device["thermostat"].get("setpoint_high")

    @property
    def target_temperature_low(self) -> float | None:
        """Return the heating temperature we try to reach in case of heating.

        Connected to the HVACMode combination AUTO/HEAT_COOL.
        """
        return self.device["thermostat"].get("setpoint_low")

    @plugwise_command
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if ATTR_HVAC_MODE in kwargs:
            raise HomeAssistantError("Changing hvac_mode via this command is not supported")

        data: dict[str, Any] = {}
        if ATTR_TEMPERATURE in kwargs:
            data["setpoint"] = kwargs.get(ATTR_TEMPERATURE)
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            data["setpoint_high"] = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        if ATTR_TARGET_TEMP_LOW in kwargs:
            data["setpoint_low"] = kwargs.get(ATTR_TARGET_TEMP_LOW)

        for _, temperature in data.items():
            if not (self._attr_min_temp <= temperature <= self._attr_max_temp):
                raise ValueError("Invalid temperature change requested")

        await self.coordinator.api.set_temperature(self.device["location"], data)

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
