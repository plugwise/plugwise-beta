#!/usr/bin/env python3
import logging
import voluptuous as vol

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers.entity import Entity

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
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    TEMP_CELSIUS,
)

from .const import (
    CONF_THERMOSTAT,
    DOMAIN,
    WATER_HEATER_ICON,
)

import homeassistant.helpers.config_validation as cv

CURRENT_HVAC_DHW = "dhw"

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Plugwise water_heater."""

    if discovery_info is None:
        return

    devices = []
    ctrl_id = None
    for device,thermostat in hass.data[DOMAIN][CONF_THERMOSTAT].items():
        _LOGGER.info('Device %s', device)
        _LOGGER.info('Water heater (Thermostat) %s', thermostat)

#        if not thermostat['heater']:
#            continue

        api = thermostat['data_connection']
        try:
            devs = await api.get_devices()
        except RuntimeError:
            _LOGGER.error("Unable to get location info from the API")
            return

        data = None
        _LOGGER.info('Dev %s', devs)
        for dev in devs:
            _LOGGER.info('Dev %s', dev)
            if dev['name'] == 'Controlled Device':
                ctrl_id = dev['id']
                dev_id = None
                name = dev['name']
                _LOGGER.info('Name %s', name)
                data = api.get_device_data(dev_id, ctrl_id)

                if data is None:
                    _LOGGER.debug("Received no data for device %s.", name)
                    return

                device = PwWaterHeater(api, dev['name'], dev_id, ctrl_id)
                if not device:
                    continue
                devices.append(device)
    async_add_entities(devices, True)

class PwWaterHeater(Entity):
    """Representation of a Plugwise water_heater."""

    def __init__(self, api, name, dev_id, ctlr_id):
        """Set up the Plugwise API."""
        self._api = api
        self._name = name
        self._dev_id = dev_id
        self._ctrl_id = ctlr_id
        self._heating_status =  None
        self._boiler_status = None
        self._dhw_status = None

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._heating_status or self._boiler_status:
            return CURRENT_HVAC_HEAT
        if self._dhw_status:
            return CURRENT_HVAC_DHW
        return CURRENT_HVAC_IDLE

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return WATER_HEATER_ICON

    def update(self):
        """Update the data from the water_heater."""
        _LOGGER.debug("Update water_heater called")
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
            return
        if 'central_heating_state' in data:
            self._heating_status =  data['central_heating_state']
        if 'boiler_state' in data:
            self._boiler_status = data['boiler_state']
        if 'dhw_state' in data:
            self._dhw_status = data['dhw_state']

