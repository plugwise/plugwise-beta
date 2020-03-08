"""Plugwise components for Home Assistant Core."""

import logging
import asyncio

import voluptuous as vol
from Plugwise_Smile.Smile import Smile

from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers import config_validation as cv

from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
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
    CONF_PORT,
    CONF_USERNAME,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_USERNAME,
    DEFAULT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_THERMOSTAT,
    THERMOSTAT_ICON,
    HEATER_ICON,

)

from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

# HVAC modes
HVAC_MODES_1 = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
HVAC_MODES_2 = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO]

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE)

PLUGWISE_CONFIG = vol.Schema(
        {
            vol.Optional(
                CONF_NAME, default=DEFAULT_NAME
            ): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(
                CONF_PORT, default=DEFAULT_PORT
            ): cv.port,
            vol.Optional(
                CONF_USERNAME, default=DEFAULT_USERNAME
            ): cv.string,
        }
)

# Read platform configuration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
        {
                vol.Optional(CONF_THERMOSTAT): vol.All(
                    cv.ensure_list,
                    [
                        vol.All(
                            cv.ensure_list, [PLUGWISE_CONFIG],
                        ),
                    ],
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


@asyncio.coroutine
async def async_setup(hass, config):
#async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Plugwise Gateways."""

    conf = config.get(DOMAIN)

    if conf is None:
        raise PlatformNotReady
        #conf = {}

    _LOGGER.info('Plugwise %s',conf)
    hass.data[DOMAIN] = {}
    #configured = configured_hosts(hass)

    if CONF_THERMOSTAT in conf:
        thermostats = conf[CONF_THERMOSTAT]

        _LOGGER.info('Plugwise Thermostats %s',thermostats)
        hass.data[DOMAIN][CONF_THERMOSTAT] = {}

        for thermostat in thermostats:
            _LOGGER.info('Plugwise Thermostat %s',thermostat)
            smile_config=thermostat[0]

        
            websession = async_get_clientsession(hass, verify_ssl=False)
            plugwise_data_connection = Smile(host=smile_config[CONF_HOST],password=smile_config[CONF_PASSWORD],websession=websession)

            _LOGGER.debug("Plugwise connecting %s",smile_config)
            if not await plugwise_data_connection.connect():
                _LOGGER.error("Failed to connect to Plugwise")
                return

            hass.data[DOMAIN]['thermostat'][smile_config[CONF_NAME]] = { 'data_connection': plugwise_data_connection }

            hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)
            _LOGGER.info('Plugwise Smile config: %s',config)
            _LOGGER.info('Plugwise Smile smile config: %s',smile_config)
    #  We should handle P1 sometime
    else:
       return False

    return True


#    hass.helpers.discovery.load_platform('climate', DOMAIN, {}, config)
#    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
#    hass.helpers.discovery.load_platform('water_heater', DOMAIN, {}, config)
#    _LOGGER.info('Config %s', hass.data[DOMAIN])


class PwThermostatSensor(Entity):
    """Representation of a Plugwise thermostat sensor."""

    def __init__(self, api, name, dev_id, ctlr_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        self._api = api
        self._name = name
        self._dev_id = dev_id
        self._ctrl_id = ctlr_id
        self._device = sensor_type[2]
        self._sensor = sensor
        self._sensor_type = sensor_type
        self._state = None

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_class(self):
        """Device class of this entity."""
        if self._sensor_type == "temperature":
            return DEVICE_CLASS_TEMPERATURE
        if self._sensor_type == "battery_level":
            return DEVICE_CLASS_BATTERY

#    @property
#    def device_state_attributes(self):
#        """Return the state attributes."""
#        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._sensor_type == "temperature":
            return self.hass.config.units.temperature_unit
        if self._sensor_type == "battery_level":
            return "%"

    @property
    def icon(self):
        """Icon for the sensor."""
        if self._sensor_type == "temperature":
            return "mdi:thermometer"
        if self._sensor_type == "battery_level":
            return "mdi:water-battery"

    def update(self):
        """Update the data from the thermostat."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
            return

        _LOGGER.info("Sensor {}".format(self._sensor))
        if self._sensor == 'boiler_temperature':
            self._state = data['boiler_temp']
        if self._sensor == 'battery_charge':
            value = data['battery']
            self._state = int(round(value * 100))

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
        if self._heating_status or self._boiler_status or self._dhw_status:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attributes = {}
        if self._dhw_status:
            attributes["domestic_hot_water"] = self._dhw_status
        return attributes

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


class PwThermostat(ClimateDevice):
    """Representation of an Plugwise thermostat."""

    def __init__(self, api, name, dev_id, ctlr_id, min_temp, max_temp):
        """Set up the Plugwise API."""
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
    def icon(self):
        """Return the icon to use in the frontend."""
        return THERMOSTAT_ICON

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

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
        
    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if (temperature is not None) and (self._min_temp < temperature < self._max_temp):
            _LOGGER.debug("Adjusting temperature to %s degrees C.", temperature)
            self._api.set_temperature(self._dev_id, self._dev_type, temperature)
        else:
            _LOGGER.error("Invalid temperature requested")

    def set_hvac_mode(self, hvac_mode):
        """Set the hvac mode."""
        _LOGGER.debug("Adjusting hvac_mode (i.e. schedule/schema): %s, %s.", hvac_mode)
        state = "false"
        if hvac_mode == HVAC_MODE_AUTO:
            state = "true"
        self._api.set_schedule_state(self._dev_id, self._last_active_schema, state)

    def set_preset_mode(self, preset_mode):
        _LOGGER.debug("Changing preset mode to %s.", preset_mode)
        """Set the preset mode."""
        self._api.set_preset(self._dev_id, self._dev_type, preset_mode)

    def update(self):
        """Update the data for this climate device."""
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

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
