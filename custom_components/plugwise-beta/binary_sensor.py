"""Plugwise Binary Sensor component for Home Assistant."""

import logging
from typing import Dict

from homeassistant.components.binary_sensor import DEVICE_CLASS_HEAT, BinarySensorDevice
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback

from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
)

from .const import (
    CURRENT_HVAC_DHW,
    DOMAIN,
    COOL_ICON,
    FLAME_ICON,
    IDLE_ICON,
    WATER_ICON,
)

BINARY_SENSOR_LIST = [
    "domestic_hot_water_state",
    "slave_boiler_state",
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if device["class"] == "heater_central":
            _LOGGER.debug("Plugwise device_class found")
            data = api.get_device_data(dev_id)
            for binary_sensor in BINARY_SENSOR_LIST:
                _LOGGER.debug("Binary_sensor: %s", binary_sensor)
                if binary_sensor in data:
                    _LOGGER.debug("Plugwise binary_sensor Dev %s", device["name"])
                    devices.append(PwBinarySensor(api, updater, binary_sensor, dev_id))
                    _LOGGER.info("Added binary_sensor.%s", binary_sensor)

    async_add_entities(devices, True)


class PwBinarySensor(BinarySensorDevice):
    """Representation of a Plugwise binary_sensor."""

    def __init__(self, api, updater, binary_sensor, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._dev_id = dev_id
        self._binary_sensor = binary_sensor
        self._is_on = False
        self._unique_id = f"{dev_id}-binary_sensor"

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
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._binary_sensor

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._binary_sensor,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._api.gateway_id),
        }

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.is_on

    @property
    def state(self):
        """Return the state of the binary sensor."""
        if self._is_on:
            return STATE_ON
        return STATE_OFF

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._binary_sensor == "domestic_hot_water_state":
            return WATER_ICON
        return FLAME_ICON

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_HEAT

    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update binary_sensor called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.error("Received no data for device %s.", self._binary_sensor)
        else:
            if self._binary_sensor in data:
                self._is_on = data[self._binary_sensor]
