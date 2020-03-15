#!/usr/bin/env python3
import logging
import voluptuous as vol
from functools import partial

from datetime import timedelta
import async_timeout
from typing import Any, Dict

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.components.climate import ClimateDevice
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.exceptions import PlatformNotReady

from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    TEMP_CELSIUS,
)

from .const import (
    CONF_THERMOSTAT,
    DOMAIN,
    THERMOSTAT_ICON,
)

from . import (
    HVAC_MODES_1,
    HVAC_MODES_2,
)

import homeassistant.helpers.config_validation as cv


SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

_LOGGER = logging.getLogger(__name__)

# Scan interval for updating climate values
# Smile communication is set using configuration directives
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile Thermostats from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]

    if api._smile_type == 'power':
        update_interval=timedelta(seconds=10)
    else:
        update_interval=timedelta(seconds=60)

    climate_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="climate",
        update_method=partial(async_safe_fetch,api),
        update_interval=update_interval
    )

    # First do a refresh to see if we can reach the hub.
    # Otherwise we will declare not ready.
    await climate_coordinator.async_refresh()

    if not climate_coordinator.last_update_success:
        raise PlatformNotReady

    devices = []
    ctrl_id = None
    data = None
    idx = 0
    _LOGGER.info('Plugwise thermostat Devices %s', climate_coordinator.data)
    if api._smile_type == 'thermostat':
       for dev in climate_coordinator.data:
          if dev['name'] == 'Controlled Device':
              ctrl_id = dev['id']
          else:
              device = PwThermostat(climate_coordinator, idx, api,dev['name'], dev['id'], ctrl_id, 4, 30)
              _LOGGER.debug("Plugwise device : %s",device)
              if not device:
                  continue
              devices.append(device)
    async_add_entities(devices, True)


async def async_safe_fetch(api):
    """Safely fetch data."""
    with async_timeout.timeout(10):
        await api.full_update_device()
        return await api.get_devices()

class PwThermostat(ClimateDevice):
    """Representation of an Plugwise thermostat."""

    def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id, min_temp, max_temp):
        """Set up the Plugwise API."""
        self.coordinator = coordinator
        self.idx = idx
        self._api = api
        self._name = name
        self._dev_id = dev_id
        self._ctrl_id = ctlr_id
        self._min_temp = min_temp
        self._max_temp = max_temp

        self._dev_type = None
        self._selected_schema = None
        self._last_active_schema = None
        self._preset_mode = None
        self._presets = None
        self._presets_list = None
        self._boiler_status = None
        self._cooling_status = None
        self._dhw_status = None
        self._heating_status = None
        self._schema_names = None
        self._schema_status = None
        self._current_temp = None
        self._thermostat_temp = None
        self._boiler_temp = None
        self._water_pressure = None
        self._schedule_temp = None
        self._hvac_mode = None

    @property
    def hvac_action(self):
        """Return the current action."""
        if self._heating_status or self._boiler_status or self._dhw_status:
            return CURRENT_HVAC_HEAT
        if self._cooling_status:
            return CURRENT_HVAC_COOL
        return CURRENT_HVAC_IDLE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return THERMOSTAT_ICON

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def is_on(self):
      """Return entity state.

      Example to show how we fetch data from coordinator.
      """
      self.coordinator.data[self.idx]['state']

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(
            self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(
            self.async_write_ha_state
        )

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attributes = {}
        if self._schema_names:
            attributes["available_schemas"] = self._schema_names
        if self._selected_schema:
            attributes["selected_schema"] = self._selected_schema
        return attributes

    @property
    def preset_modes(self):
        """
        Return the available preset modes list and make the presets with their
        temperatures available.
        """
        return self._presets_list

    @property
    def hvac_modes(self):
        """Return the available hvac modes list."""
        if self._heating_status is not None or self._boiler_status is not None:
            if self._cooling_status is not None:
                return HVAC_MODES_2
            return HVAC_MODES_1

    @property
    def hvac_mode(self):
        """Return current active hvac state."""
        if self._schema_status:
            return HVAC_MODE_AUTO
        if self._heating_status or self._boiler_status or self._dhw_status:
            if self._cooling_status:
                return HVAC_MODE_HEAT_COOL
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def target_temperature(self):
        """Return the target_temperature.
        From the XML the thermostat-value is used because it updates 'immediately'
        compared to the target_temperature-value. This way the information on the card
        is "immediately" updated after changing the preset, temperature, etc.
        """
        return self._thermostat_temp

    @property
    def preset_mode(self):
        """Return the active preset."""
        if self._presets:
            return self._preset_mode
        return None

    @property
    def current_temperature(self):
        """Return the current room temperature."""
        return self._current_temp

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
        if (temperature is not None) and (self._min_temp < temperature < self._max_temp):
            _LOGGER.debug("Set temp dev_id = %s",self._dev_id)
            await self._api.set_temperature(self._dev_id, temperature)
        else:
            _LOGGER.error("Invalid temperature requested")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the hvac mode."""
        _LOGGER.debug("Adjusting hvac_mode (i.e. schedule/schema): %s, %s.", hvac_mode)
        state = "false"
        if hvac_mode == HVAC_MODE_AUTO:
            state = "true"
        await self._api.set_schedule_state(self._dev_id, self._last_active_schema, state)

    async def async_set_preset_mode(self, preset_mode):
        _LOGGER.debug("Changing preset mode to %s.", preset_mode)
        """Set the preset mode."""
        await self._api.set_preset(self._dev_id, preset_mode)

    async def async_update(self):
        """Update the data for this climate device."""
        await self.coordinator.async_request_refresh()

        data = self._api.get_device_data(self._dev_id, self._ctrl_id)
        _LOGGER.info('Plugwise Smile device data: %s',data)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
            return

        _LOGGER.debug("Device data collected from Plugwise API")
        if 'type' in data:
            self._dev_type = data['type']
        if 'setpoint_temp' in data:
            self._thermostat_temp = data['setpoint_temp']
        if 'current_temp' in data:
            self._current_temp = data['current_temp']
        if 'boiler_temp' in data:
            self._boiler_temp = data['boiler_temp']
        if 'available_schedules' in data:
            self._schema_names = data['available_schedules']
        if 'selected_schedule' in data:
            self._selected_schema = data['selected_schedule']
            if self._selected_schema != None:
                self._schema_status = True
                self._schedule_temp = self._thermostat_temp
            else:
                self._schema_status = False
        if 'last_used' in data:
            self._last_active_schema = data['last_used']
        if 'presets' in data:
            self._presets = data['presets']
            self._presets_list = list(self._presets)
        if 'active_preset' in data:
            self._preset_mode = data['active_preset']
        if 'boiler_state' in data:
            self._boiler_status = data['boiler_state']
        if 'central_heating_state' in data:
            self._heating_status = data['central_heating_state']
        if 'cooling_state' in data:
            self._cooling_status = data['cooling_state']
        if 'dhw_state' in data:
            self._dhw_status = data['dhw_state']

