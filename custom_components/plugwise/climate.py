"""Plugwise Climate component for Home Assistant."""

import logging

from plugwise.exceptions import PlugwiseException
from plugwise.smileclasses import Thermostat

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_NONE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_NAME, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback

from .const import (
    API,
    CLIMATE_DOMAIN,
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
    SMILE,
    VENDOR,
)
from .gateway import SmileGateway

HVAC_MODES_HEAT_ONLY = [HVAC_MODE_HEAT, HVAC_MODE_AUTO, HVAC_MODE_OFF]
HVAC_MODES_HEAT_COOL = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO, HVAC_MODE_OFF]

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile Thermostats from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    smile = hass.data[DOMAIN][config_entry.entry_id][SMILE]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in smile.devices:
        if smile.devices[dev_id][PW_CLASS] not in MASTER_THERMOSTATS:
            continue

        thermostat = PwThermostat(
            api,
            coordinator,
            smile,
            smile.devices[dev_id][ATTR_NAME],
            dev_id,
            DEFAULT_MIN_TEMP,
            DEFAULT_MAX_TEMP,
        )
        entities.append(thermostat)
        _LOGGER.info(f"Added climate.{smile.devices[dev_id][ATTR_NAME]}")

    async_add_entities(entities, True)


class PwThermostat(SmileGateway, ClimateEntity):
    """Representation of a Plugwise (zone) thermostat."""

    def __init__(
        self,
        api,
        coordinator,
        smile,
        name,
        dev_id,
        min_temp,
        max_temp,
    ):
        """Set up the PwThermostat."""
        super().__init__(
            coordinator,
            dev_id,
            smile,
            name,
            smile.devices[dev_id][PW_MODEL],
            smile.devices[dev_id][VENDOR],
            smile.devices[dev_id][FW]
        )

        self._thermostat = Thermostat(api, dev_id)

        self._api = api
        self._smile = smile

        self._device_name = self._name = name
        self._last_active_schema = self._thermostat.last_active_schema
        self._loc_id = self._smile.devices[dev_id][PW_LOCATION]
        self._max_temp = max_temp
        self._min_temp = min_temp
        self._presets = self._thermostat.presets
        self._schedule_temp = self._thermostat.schedule_temperature

        self._unique_id = f"{dev_id}-{CLIMATE_DOMAIN}"

    @property
    def hvac_action(self):
        """Return the current action."""
        if self._smile.single_master_thermostat:
            if self._thermostat.heating_state:
                return CURRENT_HVAC_HEAT
            if self._thermostat.cooling_state:
                return CURRENT_HVAC_COOL
            return CURRENT_HVAC_IDLE

        if self._thermostat.target_temperature > self._thermostat.current_temperature:
                return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def hvac_mode(self):
        """Return current active hvac state."""
        return self._thermostat.hvac_mode

    @property
    def hvac_modes(self):
        """Return the available hvac modes list."""
        if self._thermostat.compressor_state is not None:
            return HVAC_MODES_HEAT_COOL
        return HVAC_MODES_HEAT_ONLY

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def extra_state_attributes(self):
        """Return the device specific state attributes."""
        return self._thermostat.extra_state_attributes

    @property
    def preset_modes(self):
        """Return the available preset modes list."""
        return self._thermostat.preset_modes

    @property
    def target_temperature(self):
        """Return the target_temperature."""
        return self._thermostat.target_temperature

    @property
    def preset_mode(self):
        """Return the active preset."""
        return self._thermostat.preset_mode

    @property
    def current_temperature(self):
        """Return the current room temperature."""
        return self._thermostat.current_temperature

    @property
    def min_temp(self):
        """Return the minimal temperature possible to set."""
        return self._min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature possible to set."""
        return self._max_temp

    @property
    def temperature_unit(self):
        """Return the unit of measured temperature."""
        return TEMP_CELSIUS

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if (temperature is not None) and (
            self._min_temp < temperature < self._max_temp
        ):
            _LOGGER.debug("Set temp to %sºC", temperature)
            try:
                await self._api.set_temperature(self._loc_id, temperature)
                self._setpoint = temperature
                self.async_write_ha_state()
            except PlugwiseException:
                _LOGGER.error("Error while communicating to device")
        else:
            _LOGGER.error("Invalid temperature requested")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the hvac mode, options are 'off', 'heat'/'heat_cool' and 'auto'."""
        _LOGGER.debug("Set hvac_mode to: %s", hvac_mode)
        state = SCHEDULE_OFF
        if hvac_mode == HVAC_MODE_AUTO:
            state = SCHEDULE_ON
            try:
                await self._api.set_temperature(self._loc_id, self._schedule_temp)
                self._setpoint = self._schedule_temp
            except PlugwiseException:
                _LOGGER.error("Error while communicating to device")
        try:
            await self._api.set_schedule_state(
                self._loc_id, self._last_active_schema, state
            )
            if hvac_mode == HVAC_MODE_OFF:
                preset_mode = PRESET_AWAY
                await self._api.set_preset(self._loc_id, preset_mode)
                self._preset_mode = preset_mode
                self._setpoint = self._presets.get(self._preset_mode, PRESET_NONE)[0]
            if hvac_mode in [HVAC_MODE_HEAT, HVAC_MODE_HEAT_COOL] and self._preset_mode == PRESET_AWAY:
                preset_mode = PRESET_HOME
                await self._api.set_preset(self._loc_id, preset_mode)
                self._preset_mode = preset_mode
                self._setpoint = self._presets.get(self._preset_mode, PRESET_NONE)[0]
            self._hvac_mode = hvac_mode
            self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        _LOGGER.debug("Set preset mode to %s", preset_mode)
        try:
            await self._api.set_preset(self._loc_id, preset_mode)
            self._preset_mode = preset_mode
            self._setpoint = self._presets.get(self._preset_mode, PRESET_NONE)[0]
            self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    @callback
    def _async_process_data(self):
        """Update the data for this climate device."""
        self._thermostat.update_data()
        self.async_write_ha_state()
