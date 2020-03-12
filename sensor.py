#!/usr/bin/env python3
import logging
import voluptuous as vol

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers.entity import Entity

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
    DEVICE_CLASS_PRESSURE,
    PRESSURE_MBAR,
)

from .const import (
    ATTR_ILLUMINANCE,
    CONF_THERMOSTAT,
    CONF_POWER,
    DOMAIN,
)

import homeassistant.helpers.config_validation as cv


DEFAULT_NAME = "Plugwise async sensoj"
DEFAULT_ICON = "mdi:thermometer"


_LOGGER = logging.getLogger(__name__)

THERMOSTAT_SENSOR_TYPES = {
    ATTR_TEMPERATURE : [TEMP_CELSIUS, None, DEVICE_CLASS_TEMPERATURE],
    ATTR_BATTERY_LEVEL : ["%" , None, DEVICE_CLASS_BATTERY],
    ATTR_ILLUMINANCE: ["lm", None, DEVICE_CLASS_ILLUMINANCE],
    "pressure" : [PRESSURE_MBAR , None, DEVICE_CLASS_PRESSURE],
}

THERMOSTAT_SENSORS_AVAILABLE = {
    "boiler_temperature": ATTR_TEMPERATURE,
    "battery_charge": ATTR_BATTERY_LEVEL,
    "outdoor_temperature": ATTR_TEMPERATURE,
    "illuminance": ATTR_ILLUMINANCE,
    "water_pressure": "pressure",
}

POWER_SENSOR_TYPES = {
    'electricity_consumed_offpeak_point': ['Current Consumed Power (off peak)', 'W', 'mdi:flash'],
    'electricity_consumed_peak_point': ['Current Consumed Power', 'W', 'mdi:flash'],
    'electricity_consumed_offpeak_cumulative': ['Cumulative Consumed Power (off peak)', 'kW', 'mdi:flash'],
    'electricity_consumed_peak_cumulative': ['Cumulative Consumed Power', 'kW', 'mdi:flash'],
    'electricity_produced_offpeak_point': ['Current Consumed Power (off peak)', 'W', 'mdi:white-balance-synny'],
    'electricity_produced_peak_point': ['Current Consumed Power', 'W', 'mdi:white-balance-synny'],
    'electricity_produced_offpeak_cumulative': ['Cumulative Consumed Power (off peak)', 'kW', 'mdi:white-balance-synny'],
    'electricity_produced_peak_cumulative': ['Cumulative Consumed Power', 'kW', 'mdi:white-balance-synny'],
    'gas_consumed_point_peak_point': ['Current Consumed Gas', 'm3', 'mdi:gas-cylinder'],
    'gas_consumed_point_peak_cumulative': ['Cumulative Consumed Gas', 'm3', 'mdigas-cylinder'],
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Plugwise Thermostat Sensor."""

    if discovery_info is None:
        return

    devices = []
    ctrl_id = None
    if CONF_THERMOSTAT in hass.data[DOMAIN]:
        for device,thermostat in hass.data[DOMAIN][CONF_THERMOSTAT].items():
            _LOGGER.info('Device %s', device)
            _LOGGER.info('Thermostat %s', thermostat)
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

                for sensor,sensor_type in THERMOSTAT_SENSORS_AVAILABLE.items():
                    addSensor=False
                    if sensor == 'boiler_temperature':
                        if 'boiler_temp' in data:
                            if data['boiler_temp']:
                                addSensor=True
                                _LOGGER.info('Adding boiler_temp')
                    if sensor == 'water_pressure':
                        if 'water_pressure' in data:
                            if data['water_pressure']:
                                addSensor=True
                                _LOGGER.info('Adding water_pressure')
                    if sensor == 'battery_charge':
                        if 'battery' in data:
                            if data['battery']:
                                addSensor=True
                                _LOGGER.info('Adding battery_charge')
                    if sensor == 'outdoor_temperature':
                        if 'outdoor_temp' in data:
                            if data['outdoor_temp']:
                                addSensor=True
                                _LOGGER.info('Adding outdoor_temperature')
                    if sensor == 'illuminance':
                        if 'illuminance' in data:
                            if data['illuminance']:
                                addSensor=True
                                _LOGGER.info('Adding illuminance')
                    if addSensor:
                        devices.append(PwThermostatSensor(api,'{}_{}'.format(name, sensor), dev_id, ctrl_id, sensor, sensor_type))

    if CONF_POWER in hass.data[DOMAIN]:
        for device,power in hass.data[DOMAIN][CONF_POWER].items():
            _LOGGER.info('Device %s', device)
            _LOGGER.info('Power %s', power)
            api = power['data_connection']
            try:
                devs = await api.get_devices()
            except RuntimeError:
                _LOGGER.error("Unable to get location info from the API")
                return

            data = None
            _LOGGER.info('Dev %s', devs)
            for dev in devs:
                _LOGGER.info('Dev %s', dev)
                if dev['name'] == 'Home':
                    ctrl_id = dev['id']
                    dev_id = None
                    name = dev['name']
                    _LOGGER.info('Name %s', name)
                    data = api.get_device_data(dev_id, ctrl_id)

                if data is None:
                    _LOGGER.debug("Received no data for device %s.", name)
                    return

                for sensor,sensor_type in POWER_SENSOR_TYPES.items():
                    _LOGGER.debug("sensor %s",sensor)
                    _LOGGER.debug("sensortype %s",sensor_type)
                    addSensor=True
                    if 'off' in sensor and api._power_tariff['electricity_consumption_tariff_structure'] == 'single':
                        addSensor=False
                    _LOGGER.debug(sensor)
                    _LOGGER.debug(power['gas'])
                    if 'gas_' in sensor and not power['gas']:
                        addSensor=False
                    if 'produced' in sensor and not power['solar']:
                        addSensor=False

                    if addSensor:
                        devices.append(PwPowerSensor(api,'{}_{}'.format(name, sensor), dev_id, ctrl_id, sensor, sensor_type))

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
        if self._sensor_type == "illuminance":
            return DEVICE_CLASS_ILLUMINANCE
        if self._sensor_type == "pressure":
            return DEVICE_CLASS_PRESSURE

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
        if self._sensor_type == "illuminance":
            return "lm"
        if self._sensor_type == "pressure":
            return PRESSURE_MBAR

    @property
    def icon(self):
        """Icon for the sensor."""
        if self._sensor_type == "temperature":
            return "mdi:thermometer"
        if self._sensor_type == "battery_level":
            return "mdi:water-battery"
        if self._sensor_type == "illuminance":
            return "mdi:lightbulb-on-outline"
        if self._sensor_type == "pressure":
            return "mdi:water"

    def update(self):
        """Update the data from the thermostat."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
            return

        _LOGGER.info("Sensor {}".format(self._sensor))
        if self._sensor == 'boiler_temperature':
            if 'boiler_temp' in data:
                self._state = data['boiler_temp']
        if self._sensor == 'water_pressure':
            if 'water_pressure' in data:
                self._state = data['water_pressure']
        if self._sensor == 'battery_charge':
            if 'battery' in data:
                value = data['battery']
                self._state = int(round(value * 100))
        if self._sensor == 'outdoor_temperature':
            if 'outdoor_temp' in data:
                self._state = data['outdoor_temp']
        if self._sensor == 'illuminance':
            if 'illuminance' in data:
                self._state = data['illuminance']

class PwPowerSensor(Entity):
    """Representation of a Plugwise power sensor P1."""

    def __init__(self, api, name, dev_id, ctlr_id, sensor, sensor_type):
        """Initialize the sensor."""
        self._api = api
        self._name = name
        self._dev_id = dev_id
        self._ctrl_id = ctlr_id
        self._device = sensor_type[0]
        self._unit_of_measurement = sensor_type[1]
        self._icon = sensor_type[2]
        self._sensor = sensor
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Update the data from the thermostat."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)

        _LOGGER.info("Sensor {}".format(self._sensor))

        if self._sensor in data:
            measurement = data[self._sensor]
            if 'cumulative' in self._sensor:
                measurement = int(data[self._sensor]/1000)
            self._state = measurement


