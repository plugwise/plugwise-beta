#!/usr/bin/env python3
import logging 
import voluptuous as vol

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers.entity import Entity

from homeassistant.components.climate.const import (
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ILLUMINANCE,
)

from .const import (
    ATTR_ILLUMINANCE,
    CONF_THERMOSTAT,
    DOMAIN,
)

import homeassistant.helpers.config_validation as cv


SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

DEFAULT_NAME = "Plugwise async Dev Thermostat"
DEFAULT_ICON = "mdi:thermometer"


_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    ATTR_TEMPERATURE : [TEMP_CELSIUS, None, DEVICE_CLASS_TEMPERATURE],
    ATTR_BATTERY_LEVEL : ["%" , None, DEVICE_CLASS_BATTERY],
    ATTR_ILLUMINANCE: ["lm", None, DEVICE_CLASS_ILLUMINANCE],
}

SENSOR_AVAILABLE = {
    "boiler_temperature": ATTR_TEMPERATURE,
    "battery_charge": ATTR_BATTERY_LEVEL,
    "outdoor_temperature": ATTR_TEMPERATURE,
    "illuminance": ATTR_ILLUMINANCE,
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Plugwise Thermostat Sensor."""

    if discovery_info is None:
        return

    devices = []
    ctrl_id = None
    for device,thermostat in hass.data[DOMAIN][CONF_THERMOSTAT].items():
        _LOGGER.info('Device %s', device)
        _LOGGER.info('Thermostat %s', thermostat)
        api = thermostat['data_connection']
        try:
            devs = api.get_devices()
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
            else:
                name = dev['name']
                dev_id = dev['id']
                _LOGGER.info('Name %s', name)
                data = api.get_device_data(dev_id, ctrl_id)

            if data is None:
                _LOGGER.debug("Received no data for device %s.", name)
                return

            #_LOGGER.debug("Device data %s.", data)
            # data {'type': 'thermostat', 'battery': None, 'setpoint_temp': 22.0, 'current_temp': 21.7, 'active_preset': 'home', 'presets': {'vacation': [15.0, 0], 'no_frost': [10.0, 0], 'asleep': [16.0, 0], 'away': [16.0, 0], 'home': [21.0, 0]}, 'available_schedules': ['Test', 'Thermostat schedule', 'Normaal'], 'selected_schedule': 'Normaal', 'last_used': 'Test', 'boiler_state': None, 'central_heating_state': False, 'cooling_state': None, 'dhw_state': None, 'outdoor_temp': '9.3', 'illuminance': '0.8'}.

            for sensor,sensor_type in SENSOR_AVAILABLE.items():
                addSensor=False
                if sensor == 'boiler_temperature':
                    if 'boiler_temp' in data:
                        if data['boiler_temp']:
                            addSensor=True
                            _LOGGER.info('Adding boiler_temp')
                if sensor == 'battery_charge':
                    if 'battery' in data:
                        if data['battery']:
                            addSensor=True
                            _LOGGER.info('Adding battery_charge')
                if sensor == 'outdoor_temperature':
                    if 'outdoor_temp' in data:
                        if data['outdoor_temp']:
                            addSensor=True
                            sensor='outdoor_temp'
                            _LOGGER.info('Adding outdoor_temperature')
                if sensor == 'illuminance':
                    if 'illuminance' in data:
                        if data['illuminance']:
                            addSensor=True
                            _LOGGER.info('Adding illuminance')
                if addSensor:
                    devices.append(PwThermostatSensor(api,'{}_{}'.format(name, sensor), dev_id, ctrl_id, sensor, sensor_type))
    async_add_entities(devices, True)

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
        if self._sensor == 'outdoor_temp':
            self._state = data['outdoor_temp']
        if self._sensor == 'illuminance':
            self._state = data['illuminance']

