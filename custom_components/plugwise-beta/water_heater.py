#!/usr/bin/env python3
import logging
from typing import Dict

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, WATER_HEATER_ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if device["class"] == "heater_central":
            data = api.get_device_data(dev_id)
            if "domestic_hot_water_state" in data:
                if data["domestic_hot_water_state"] is not None:
                    _LOGGER.info("Plugwise water_heater Dev %s", device["name"])
                    water_heater = PwWaterHeater(api, updater, device["name"], dev_id)
                    devices.append(water_heater)
                    _LOGGER.info("Added water_heater.%s", "{}".format(device["name"]))

    async_add_entities(devices, True)


class PwWaterHeater(Entity):
    """Representation of a Plugwise water_heater."""

    def __init__(self, api, updater, name, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._domestic_hot_water_state = None
        self._unique_id = f"{dev_id}-water_heater"

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
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._api._gateway_id),
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._domestic_hot_water_state:
            return STATE_ON
        return STATE_OFF

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return WATER_HEATER_ICON

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    def update(self):
        """Update the entity."""

        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            if "domestic_hot_water_state" in data:
                self._domestic_hot_water_state = (
                    data["domestic_hot_water_state"] == "on"
                )
