#!/usr/bin/env python3
import logging
import voluptuous as vol
from functools import partial

from datetime import timedelta
import async_timeout
from typing import Any, Dict

from Plugwise_Smile.Smile import Smile

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.exceptions import PlatformNotReady

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
    DEVICE_CLASS_POWER,
    PRESSURE_MBAR,
)

from .const import (
    ATTR_ILLUMINANCE,
    CONF_THERMOSTAT,
    CONF_POWER,
    DOMAIN,
    DEVICE_CLASS_GAS,
)

import homeassistant.helpers.config_validation as cv


DEFAULT_NAME = "Plugwise async sensor"
DEFAULT_ICON = "mdi:thermometer"



_LOGGER = logging.getLogger(__name__)

ATTR_TEMPERATURE = [TEMP_CELSIUS, None, DEVICE_CLASS_TEMPERATURE,"mdi:thermometer"]
ATTR_BATTERY_LEVEL = ["%" , None, DEVICE_CLASS_BATTERY,"mdi:water-battery"]
ATTR_ILLUMINANCE = ["lm", None, DEVICE_CLASS_ILLUMINANCE,"mdi:lightbulb-on-outline"]
ATTR_PRESSURE = [PRESSURE_MBAR , None, DEVICE_CLASS_PRESSURE, "mdi:water"]
SENSOR_MAP = {
    'thermostat': ATTR_TEMPERATURE,
    'temperature': ATTR_TEMPERATURE,
    'battery': ATTR_BATTERY_LEVEL,
    'battery_charge': ATTR_BATTERY_LEVEL,
    'temperature_difference': ATTR_TEMPERATURE,
    'electricity_consumed': ['Current Consumed Power', 'W', DEVICE_CLASS_POWER, 'mdi:flash'],
    'electricity_produced': ['Current Produced Power', 'W', DEVICE_CLASS_POWER, 'mdi:flash'],
    'outdoor_temperature': ATTR_TEMPERATURE,
    'central_heater_water_pressure': ATTR_PRESSURE,
    'illuminance': ATTR_ILLUMINANCE,
    'boiler_temperature': ATTR_TEMPERATURE,
    'electricity_consumed_off_peak_point': ['Current Consumed Power (off peak)', 'W', DEVICE_CLASS_POWER, "mdi:flash"],
    'electricity_consumed_peak_point': ['Current Consumed Power', 'W', DEVICE_CLASS_POWER, "mdi:flash"],
    'electricity_consumed_off_peak_cumulative': ['Cumulative Consumed Power (off peak)', 'kW', DEVICE_CLASS_POWER, "mdi:flash"],
    'electricity_consumed_peak_cumulative': ['Cumulative Consumed Power', 'kW', DEVICE_CLASS_POWER, "mdi:flash"],
    'electricity_produced_off_peak_point': ['Current Consumed Power (off peak)', 'W', DEVICE_CLASS_POWER, "mdi:white-balancy-sunny"],
    'electricity_produced_peak_point': ['Current Consumed Power', 'W', DEVICE_CLASS_POWER, "mdi:white-balancy-sunny"],
    'electricity_produced_off_peak_cumulative': ['Cumulative Consumed Power (off peak)', 'kW', DEVICE_CLASS_POWER, "mdi:white-balancy-sunny"],
    'electricity_produced_peak_cumulative': ['Cumulative Consumed Power', 'kW', DEVICE_CLASS_POWER, "mdi:white-balancy-sunny"],
    'gas_consumed_point_peak_point': ['Current Consumed Gas', 'm3', DEVICE_CLASS_GAS, "mdi:gas-cylinder"],
    'gas_consumed_point_peak_cumulative': ['Cumulative Consumed Gas', 'm3', DEVICE_CLASS_GAS, "mdi:gas-cylinder"],
}

# TODO:
#    'relay',
#    'valve_position',
#    'boiler_state',
#    'central_heating_state',
#    'cooling_state',
#    'dhw_state',

# TODO:
#    'electricity_consumption_tariff_structure',
#    'electricity_consumption_peak_tariff',
#    'electricity_consumption_off_peak_tariff',
#    'electricity_production_peak_tariff',
#    'electricity_production_off_peak_tariff',
#    'electricity_consumption_single_tariff',
#    'electricity_production_single_tariff',
#    'gas_consumption_tariff',

# Scan interval for updating sensor values
# Smile communication is set using configuration directives
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug('Plugwise hass data %s',hass.data[DOMAIN])
    api = hass.data[DOMAIN][config_entry.entry_id]['api']
    updater = hass.data[DOMAIN][config_entry.entry_id]['updater']

#    # Stay close to meter measurements for power, for thermostat back off a bit
#    if api._smile_type == 'power':
#        update_interval=timedelta(seconds=10)
#    else:
#        update_interval=timedelta(seconds=60)
#
#    sensor_coordinator = DataUpdateCoordinator(
#        hass,
#        _LOGGER,
#        name="sensor",
#        update_method=partial(async_safe_fetch,api),
#        update_interval=update_interval
#    )
#
#    # First do a refresh to see if we can reach the hub.
#    # Otherwise we will declare not ready.
#    await sensor_coordinator.async_refresh()
#
#    if not sensor_coordinator.last_update_success:
#        raise PlatformNotReady

    _LOGGER.debug('Plugwise sensor type %s',api._smile_type)
#    _LOGGER.debug('Plugwise sensor Sensorcoordinator %s',sensor_coordinator)
#    _LOGGER.debug('Plugwise sensor Sensorcoordinator data %s',sensor_coordinator.data)

    devices = []
    all_devices=api.get_all_devices()
    for dev_id,device in all_devices.items():
        data = api.get_device_data(dev_id)
        _LOGGER.info('Plugwise sensor Dev %s', device['name'])
        # Skip thermostats since they'll include in climate
        # if 'thermostat' not in device['types']:
        if True:
            for sensor,sensor_type in SENSOR_MAP.items():
                if sensor in data:
                    if data[sensor] is not None:
                        #_LOGGER.info('Plugwise sensor is %s for %s (%s)',sensor,dev_id,device)
                        #_LOGGER.info('Plugwise sensor data %s for %s',data,dev_id)
                        if 'power' in device['types']:
                            if 'off' in sensor and api._power_tariff['electricity_consumption_tariff_structure'] == 'single':
                                continue
                            devices.append(PwPowerSensor(api, updater, '{}_{}'.format(device['name'], sensor), dev_id, sensor, sensor_type))

                        devices.append(PwThermostatSensor(api, updater, '{}_{}'.format(device['name'], sensor), dev_id, sensor, sensor_type))
                        _LOGGER.info('Added sensor.%s', '{}_{}'.format(device['name'], sensor))

    async_add_entities(devices, True)

class PwThermostatSensor(Entity):
    """Safely fetch data."""

    # def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id, sensor, sensor_type):
    def __init__(self, api, updater, name, dev_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._device = sensor_type[2]
        self._sensor = sensor
        self._sensor_type = sensor_type
        self._unit_of_measurement = sensor_type[1]
        self._icon = sensor_type[3]
        self._class = sensor_type[2]
        self._state = None
        self._unique_id = f"{dev_id}-{name}-{sensor_type[2]}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._updater.async_add_listener(self._update_callback)

    async def async_will_remove_from_hass(self):
        """Disconnect callbacks."""
        self._updater.async_remove_listener(self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.update()
        self.async_write_ha_state()

    @property
    def device_class(self):
        """Device class of this entity."""
        return self._class

    @property
    def should_poll(self):
        """Return False, updates are controlled via the hub."""
        return False

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._api._gateway_id),
        }

#    @property
#    def device_state_attributes(self):
#        """Return the state attributes."""
#        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon for the sensor."""
        return self._icon

    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            if self._sensor in data:
                if data[self._sensor] is not None:
                    measurement = data[self._sensor]
                    self._state = measurement


#async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#    """Add the Plugwise Thermostat Sensor."""
#
#    if discovery_info is None:
#        return
#
#
#
#    async_add_entities(devices, True)

class PwPowerSensor(Entity):
    """Safely fetch data."""

    # def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id, sensor, sensor_type):
    def __init__(self, api, updater, name, dev_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._device = sensor_type[0]
        self._unit_of_measurement = sensor_type[1]
        self._icon = sensor_type[3]
        self._class = sensor_type[2]
        self._sensor = sensor
        self._state = None
        self._unique_id = f"{dev_id}-{name}-{sensor_type[2]}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._updater.async_add_listener(self._update_callback)

    async def async_will_remove_from_hass(self):
        """Disconnect callbacks."""
        self._updater.async_remove_listener(self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.update()
        self.async_write_ha_state()

    @property
    def should_poll(self):
        """Return False, updates are controlled via the hub."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_class(self):
        """Device class of this entity."""
        return self._class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Update the entity."""

        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            #_LOGGER.info("Sensor {}_{}".format(self._name, self._sensor))
            if self._sensor in data:
                if data[self._sensor] is not None:
                    measurement = data[self._sensor]
                    #_LOGGER.debug("Sensor value: %s", measurement)
                    if self._unit_of_measurement == 'kW':
                        measurement = int(measurement/1000)
                    self._state = measurement
