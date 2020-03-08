#!/usr/bin/env python3
import logging 
import voluptuous as vol

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateDevice

from homeassistant.components.climate.const import (
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
)

from . import (
    PwThermostat,
)

import homeassistant.helpers.config_validation as cv


SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

DEFAULT_NAME = "Plugwise async Dev Thermostat"
DEFAULT_ICON = "mdi:thermometer"


# Read platform configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_HOST): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Plugwise ClimateDevice."""

    if discovery_info is None:
        return

    devices = []
    ctrl_id = None
    for device,thermostat in hass.data[DOMAIN][CONF_THERMOSTAT].items():
        _LOGGER.info('Device %s',device)
        _LOGGER.info('Thermostat %s',thermostat)
        devs = thermostat['data_connection'].get_devices()
        _LOGGER.debug("Plugwise devs : %s",devs)
        try:
            devs = thermostat['data_connection'].get_devices()
            _LOGGER.debug("Plugwise devs : %s",devs)
        except RuntimeError:
            _LOGGER.error("Unable to get location info from the API")
            return
        
        for dev in devs:
            if dev['name'] == 'Controlled Device':
                ctrl_id = dev['id']
            else:
                device = PwThermostat(thermostat['data_connection'], dev['name'], dev['id'], ctrl_id, 4, 30)
                _LOGGER.debug("Plugwise device : %s",device)
                if not device:
                    continue
                devices.append(device)
    async_add_entities(devices, True)

#    _LOGGER.info('Plugwise hassdata %s',hass.data[DOMAIN])
#    _LOGGER.info('Plugwise data loop %s',hass.data[DOMAIN][CONF_THERMOSTAT])
#    # hass.data[DOMAIN][smile_config[CONF_NAME]]
#    devices = []
#    for device,connections in hass.data[DOMAIN].items():
#      for thermostat,api in connections.items():
#        _LOGGER.info('Plugwise Device %s',device)
#        _LOGGER.info('Plugwise Thermostat %s',thermostat)
#        _LOGGER.info('Plugwise API %s',api)
#        devices.append(
#            PwThermostat(
#                api['data_connection'],
#                '{}_{}'.format(device,CONF_THERMOSTAT),
#                min_temp=4,max_temp=30,
#                #config[CONF_MIN_TEMP],
#                #config[CONF_MAX_TEMP],
#            )
#        )
#    async_add_entities(devices, True)

#    plugwise_data_connection = Smile(host=config[CONF_HOST],password=config[CONF_PASSWORD],websession=async_get_clientsession(hass))
#
#    if not await plugwise_data_connection.connect():
#        _LOGGER.error("Failed to connect to Plugwise")
#        return

##    await plugwise_data_connection.find_all_appliances()
#
##    await plugwise_data_connection.update_domain_objects()
#
##    data = plugwise_data_connection.get_current_preset()
##    _LOGGER.debug("Plugwise current preset; %s", data)
##    data = plugwise_data_connection.get_current_temperature()
##    _LOGGER.debug("Plugwise current temperature; %s", data)
##    data = plugwise_data_connection.get_schedule_temperature()
##    _LOGGER.debug("Plugwise schedule temperature; %s", data)
#
#    dev = []
#    dev.append(PlugwiseAnna(plugwise_data_connection,config[CONF_NAME]))
#    async_add_entities(dev)


## #class PlugwiseAnna(ClimateDevice):
## #    """Representation of the Smile/Anna thermostat."""
## #
## #    def __init__(self, plugwise_data_connection, name):
## #        """Set up the Plugwise API."""
## #        self._conn = plugwise_data_connection
## #        self._name = name
## #        self._hvac_mode = None
## #
## #    @property
## #    def supported_features(self):
## #        """Return the list of supported features."""
## #        return SUPPORT_FLAGS
## #
## #    @property
## #    def icon(self):
## #        """Return the icon to use in the frontend."""
## #        return DEFAULT_ICON
## #
## #    @property
## #    def name(self):
## #        """Return the name of the entity."""
## #        return self._name
## #
## #    @property
## #    def temperature_unit(self):
## #        """Return the unit of measurement which this thermostat uses."""
## #        return TEMP_CELSIUS
## #
## #    @property
## #    def target_temperature(self):
## #        """Return the temperature we try to reach."""
## #        return self._conn.get_schedule_temperature()
## #
## #    @property
## #    def current_temperature(self):
## #        """Return the current temperature."""
## #        return self._conn.get_current_temperature()
## #
## #    @property
## #    def preset_mode(self):
## #        return self._conn.get_current_preset()
## #
## #    @property
## #    def hvac_modes(self):
## #        return None
## #
## #    @property
## #    def hvac_mode(self):
## #        return None
## #
## #    @property
## #    def preset_modes(self):
## #        return None
## #
## #    async def async_update(self):
## #        """Retrieve latest state."""
## #        _LOGGER.debug("Plugwise updating")
## #        self = await self._conn.update_device()
