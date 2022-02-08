"""Plugwise Climate component for Home Assistant."""

import logging

from plugwise.exceptions import PlugwiseException
from plugwise.smile import Smile

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_HOME,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, ATTR_TEMPERATURE, Platform, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import (
    API,
    COORDINATOR,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DOMAIN,
    FW,
    MASTER_THERMOSTATS,
    PW_CLASS,
    PW_LOCATION,
    PW_MODEL,
    SCHEDULE_OFF,
    SCHEDULE_ON,
    VENDOR,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseGatewayEntity
from .gateway import SmileGateway
from .smile_helpers import GWThermostat, get_preset_temp

HVAC_MODES_HEAT_ONLY = [HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF]
HVAC_MODES_HEAT_COOL = [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_OFF]

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile Thermostats from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[PwThermostat] = []
    for dev_id in coordinator.data[1]:
        if coordinator.data[1][dev_id][PW_CLASS] not in MASTER_THERMOSTATS:
            continue

        thermostat = PwThermostat(
            api,
            coordinator,
            ClimateEntityDescription(
                key=f"{dev_id}_thermostat",
                name=coordinator.data[1][dev_id].get(ATTR_NAME),
            ),
            dev_id,
            DEFAULT_MAX_TEMP,
            DEFAULT_MIN_TEMP,
        )
        entities.append(thermostat)
        _LOGGER.info(
            "Added %s climate entity", coordinator.data[1][dev_id].get(ATTR_NAME)
        )

    async_add_entities(entities, True)


class PlugwiseClimateEntity(PlugwiseGatewayEntity, ClimateEntity):
    """Representation of a Plugwise (zone) thermostat."""

    def __init__(
        self,
        api: Smile,
        coordinator: PlugwiseDataUpdateCoordinator,
        description: ClimateEntityDescription,
        dev_id: str,
        max_temp: str,
        min_temp: str,
    ) -> None:
        """Set up the PwThermostat."""
        super().__init__(
            coordinator,
            description,
            dev_id,
            coordinator.data[1][dev_id].get(PW_MODEL),
            description.name,
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
        )

        self._gw_thermostat = GWThermostat(coordinator.data, dev_id)

        self._attr_device_class = None
        self._attr_max_temp = max_temp
        self._attr_min_temp = min_temp
        self._attr_name = description.name
        self._attr_supported_features = SUPPORT_FLAGS
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_unique_id = f"{dev_id}-{Platform.CLIMATE}"

        self._api = api
        self._cooling_present = coordinator.data[0].get("cooling_present")
        self._data = coordinator.data[1].get(dev_id)
        self._dev_id = dev_id
        self._loc_id = coordinator.data[1][dev_id].get(PW_LOCATION)

    @property
    def current_temperature(self):
        """Climate current measured temperature."""
        return self._data["sensors"].get("temperature")

    @property
    def hvac_action(self):
        """Return the current action."""
        if self._gw_thermostat.heating_state:
            return CURRENT_HVAC_HEAT
        if self._gw_thermostat.cooling_state:
            return CURRENT_HVAC_COOL

        return CURRENT_HVAC_IDLE

    @property
    def hvac_modes(self):
        """Return the available hvac modes list."""
        if self._cooling_present:
            return HVAC_MODES_HEAT_COOL
        return HVAC_MODES_HEAT_ONLY

    @property
    def hvac_mode(self):
        """Return the active hvac mode."""
        return self._data.get("mode")

    @property
    def preset_mode(self):
        """Climate active preset mode."""
        return self._data.get("active_preset")

    @property
    def preset_modes(self):
        """Climate list of presets."""
        return self._data.get("preset_modes")

    @property
    def target_temperature(self):
        """Climate target temperature."""
        return self._data["sensors"].get("setpoint")

    @property
    def extra_state_attributes(self):
        """Climate extra state attributes."""
        attributes = {}
        schema_names = self._data.get("available_schedules")
        selected_schema = self._data.get("selected_schedule")
        if schema_names:
            attributes["available_schemas"] = schema_names
        if selected_schema:
            attributes["selected_schema"] = selected_schema

        return attributes

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if (temperature is not None) and (
            self._attr_min_temp < temperature < self._attr_max_temp
        ):
            try:
                await self._api.set_temperature(self._loc_id, temperature)
                self._data["sensors"]["setpoint"] = temperature
                self.async_write_ha_state()
                _LOGGER.debug("Set temperature to %s ºC", temperature)
            except PlugwiseException:
                _LOGGER.error("Error while communicating to device")
        else:
            _LOGGER.error("Invalid temperature requested")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the hvac mode, options are 'off', 'heat', 'cool' and 'auto'."""
        state = SCHEDULE_OFF
        if hvac_mode == HVAC_MODE_AUTO:
            state = SCHEDULE_ON
            schedule_temp = self._data.get("schedule_temperature")
            self._data["sensors"]["setpoint"] = schedule_temp

        try:
            await self._api.set_schedule_state(
                self._loc_id, self._data["last_used"], state
            )
            self._data["mode"] = hvac_mode
            self.async_write_ha_state()
            _LOGGER.debug("Set hvac_mode to %s", hvac_mode)
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

        # Feature request - mimic HomeKit behavior
        if hvac_mode == HVAC_MODE_OFF:
            await self.async_set_preset_mode(PRESET_AWAY)
        if (
            hvac_mode in [HVAC_MODE_HEAT, HVAC_MODE_COOL]
            and self._data["active_preset"] == PRESET_AWAY
        ):
            await self.async_set_preset_mode(PRESET_HOME)

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        try:
            await self._api.set_preset(self._loc_id, preset_mode)
            self._data["active_preset"] = preset_mode
            self._data["sensors"]["setpoint"] = get_preset_temp(
                preset_mode, self._gw_thermostat.cooling_active, self._data
            )
            self.async_write_ha_state()
            _LOGGER.debug("Set preset_mode to %s", preset_mode)
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")
