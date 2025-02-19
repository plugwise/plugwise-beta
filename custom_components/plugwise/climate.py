"""Plugwise Climate component for Home Assistant."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    PRESET_AWAY,  # pw-beta homekit emulation
    PRESET_HOME,  # pw-beta homekit emulation
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_NAME,
    ATTR_TEMPERATURE,
    STATE_OFF,
    STATE_ON,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ACTIVE_PRESET,
    AVAILABLE_SCHEDULES,
    CLIMATE_MODE,
    CONF_HOMEKIT_EMULATION,  # pw-beta homekit emulation
    CONTROL_STATE,
    DEV_CLASS,
    DOMAIN,
    LOCATION,
    LOGGER,
    LOWER_BOUND,
    MASTER_THERMOSTATS,
    REGULATION_MODES,
    RESOLUTION,
    SELECT_REGULATION_MODE,
    SENSORS,
    TARGET_TEMP,
    TARGET_TEMP_HIGH,
    TARGET_TEMP_LOW,
    THERMOSTAT,
    UPPER_BOUND,
)
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Plugwise thermostats from a config entry."""
    coordinator = entry.runtime_data
    homekit_enabled: bool = entry.options.get(
        CONF_HOMEKIT_EMULATION, False
    )  # pw-beta homekit emulation

    @callback
    def _add_entities() -> None:
        """Add Entities during init and runtime."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseClimateEntity] = []
        gateway_name = coordinator.api.smile_name
        for device_id in coordinator.new_devices:
            device = coordinator.data[device_id]
            if gateway_name == "Adam":
                if device[DEV_CLASS] == "climate":
                    entities.append(
                        PlugwiseClimateEntity(
                            coordinator, device_id, homekit_enabled
                        )  # pw-beta homekit emulation
                    )
                    LOGGER.debug("Add climate %s", device[ATTR_NAME])
            elif device[DEV_CLASS] in MASTER_THERMOSTATS:
                entities.append(
                    PlugwiseClimateEntity(
                        coordinator, device_id, homekit_enabled
                    )  # pw-beta homekit emulation
                )
                LOGGER.debug("Add climate %s", device[ATTR_NAME])

        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseClimateEntity(PlugwiseEntity, ClimateEntity):
    """Representation of a Plugwise thermostat."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = DOMAIN
    _enable_turn_on_off_backwards_compatibility = False

    _previous_mode: str = HVACAction.HEATING  # Upstream
    _homekit_mode: str | None = None  # pw-beta homekit emulation + intentional unsort

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        homekit_enabled: bool,  # pw-beta homekit emulation
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)

        gateway_id: str = coordinator.api.gateway_id
        self._gateway_data = coordinator.data[gateway_id]
        self._homekit_enabled = homekit_enabled  # pw-beta homekit emulation

        self._location = device_id
        if (location := self.device.get(LOCATION)) is not None:
            self._location = location

        self._attr_max_temp = min(self.device[THERMOSTAT][UPPER_BOUND], 35.0)
        self._attr_min_temp = self.device[THERMOSTAT][LOWER_BOUND]
        # Ensure we don't drop below 0.1
        self._attr_target_temperature_step = max(
            self.device[THERMOSTAT][RESOLUTION], 0.1
        )
        self._attr_unique_id = f"{device_id}-climate"

        # Determine supported features
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        if (
            self.coordinator.api.cooling_present
            and coordinator.api.smile_name != "Adam"
        ):
            self._attr_supported_features = (
                ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
            )
        if HVACMode.OFF in self.hvac_modes:
            self._attr_supported_features |= (
                ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
            )
        if presets := self.device["preset_modes"]:  # can be NONE
            self._attr_supported_features |= ClimateEntityFeature.PRESET_MODE
        self._attr_preset_modes = presets

    def _previous_action_mode(self, coordinator: PlugwiseDataUpdateCoordinator) -> None:
        """Return the previous action-mode when the regulation-mode is not heating or cooling.

        Helper for set_hvac_mode().
        """
        # When no cooling available, _previous_mode is always heating
        if (
            REGULATION_MODES in self._gateway_data
            and HVACAction.COOLING in self._gateway_data[REGULATION_MODES]
        ):
            mode = self._gateway_data[SELECT_REGULATION_MODE]
            if mode in (HVACAction.COOLING, HVACAction.HEATING):
                self._previous_mode = mode

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.device[SENSORS][ATTR_TEMPERATURE]

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach.

        Connected to the HVACMode combination of AUTO-HEAT.
        """

        return self.device[THERMOSTAT][TARGET_TEMP]

    @property
    def target_temperature_high(self) -> float:
        """Return the temperature we try to reach in case of cooling.

        Connected to the HVACMode combination of AUTO-HEAT_COOL.
        """
        return self.device[THERMOSTAT][TARGET_TEMP_HIGH]

    @property
    def target_temperature_low(self) -> float:
        """Return the heating temperature we try to reach in case of heating.

        Connected to the HVACMode combination AUTO-HEAT_COOL.
        """
        return self.device[THERMOSTAT][TARGET_TEMP_LOW]

    @property
    def hvac_mode(self) -> HVACMode:
        """Return HVAC operation ie. auto, cool, heat, heat_cool, or off mode."""
        if (
            mode := self.device[CLIMATE_MODE]
        ) is None or mode not in self.hvac_modes:  # pw-beta add to Core
            return HVACMode.HEAT  # pragma: no cover
        # pw-beta homekit emulation
        if self._homekit_enabled and self._homekit_mode == HVACMode.OFF:
            mode = HVACMode.OFF  # pragma: no cover

        return HVACMode(mode)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return a list of available HVACModes."""
        hvac_modes: list[HVACMode] = []
        if (
            self._homekit_enabled  # pw-beta homekit emulation
            or REGULATION_MODES in self._gateway_data
        ):
            hvac_modes.append(HVACMode.OFF)

        if AVAILABLE_SCHEDULES in self.device:
            hvac_modes.append(HVACMode.AUTO)

        if self.coordinator.api.cooling_present:
            if REGULATION_MODES in self._gateway_data:
                if self._gateway_data[SELECT_REGULATION_MODE] == HVACAction.COOLING:
                    hvac_modes.append(HVACMode.COOL)
                if self._gateway_data[SELECT_REGULATION_MODE] == HVACAction.HEATING:
                    hvac_modes.append(HVACMode.HEAT)
            else:
                hvac_modes.append(HVACMode.HEAT_COOL)
        else:
            hvac_modes.append(HVACMode.HEAT)

        return hvac_modes

    @property
    def hvac_action(self) -> HVACAction:  # pw-beta add to Core
        """Return the current running hvac operation if supported."""
        # Keep track of the previous action-mode
        self._previous_action_mode(self.coordinator)

        if (action := self.device.get(CONTROL_STATE)) is not None:
            return HVACAction(action)

        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self.device[ACTIVE_PRESET]

    @plugwise_command
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        data: dict[str, Any] = {}
        if ATTR_TEMPERATURE in kwargs:
            data[TARGET_TEMP] = kwargs.get(ATTR_TEMPERATURE)
        if ATTR_TARGET_TEMP_HIGH in kwargs:
            data[TARGET_TEMP_HIGH] = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        if ATTR_TARGET_TEMP_LOW in kwargs:
            data[TARGET_TEMP_LOW] = kwargs.get(ATTR_TARGET_TEMP_LOW)

        # Upstream removed input-valid check

        if mode := kwargs.get(ATTR_HVAC_MODE):
            await self.async_set_hvac_mode(mode)

        await self.coordinator.api.set_temperature(self._location, data)

    @plugwise_command
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the hvac mode."""
        if hvac_mode not in self.hvac_modes:
            raise HomeAssistantError("Unsupported hvac_mode")

        if hvac_mode == self.hvac_mode:
            return

        if hvac_mode != HVACMode.OFF:
            await self.coordinator.api.set_schedule_state(
                self._location,
                STATE_ON if hvac_mode == HVACMode.AUTO else STATE_OFF,
            )

        if (
            not self._homekit_enabled
        ):  # pw-beta: feature request - mimic HomeKit behavior
            if hvac_mode == HVACMode.OFF:
                await self.coordinator.api.set_regulation_mode(hvac_mode)
            elif self.hvac_mode == HVACMode.OFF:
                await self.coordinator.api.set_regulation_mode(self._previous_mode)
        else:
            self._homekit_mode = hvac_mode  # pragma: no cover
            if self._homekit_mode == HVACMode.OFF:  # pragma: no cover
                await self.async_set_preset_mode(PRESET_AWAY)  # pragma: no cover
            if (
                self._homekit_mode in [HVACMode.HEAT, HVACMode.HEAT_COOL]
                and self.device[ACTIVE_PRESET] == PRESET_AWAY
            ):  # pragma: no cover
                await self.async_set_preset_mode(PRESET_HOME)  # pragma: no cover

    @plugwise_command
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        await self.coordinator.api.set_preset(self._location, preset_mode)
