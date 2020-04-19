"""Plugwise Water Heater component for Home Assistant."""

import logging
from typing import Dict

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

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
)

INDICATE_ACTIVE_LOCAL_DEVICE = [
    "boiler_state",
    "cooling_state",
    "flame_state",
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    devices = []
    idx = 1
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if device["class"] == "heater_central":
            data = api.get_device_data(dev_id)
            for state in INDICATE_ACTIVE_LOCAL_DEVICE:
                if state in data:
                    if idx == 1:
                        _LOGGER.debug("Plugwise water_heater Dev %s", device["name"])
                        water_heater = PwWaterHeater(
                            api, updater, device["name"], dev_id
                        )
                        devices.append(water_heater)
                        _LOGGER.info(
                            "Added water_heater.%s", "{}".format(device["name"])
                        )
                        idx += 1

    async_add_entities(devices, True)


class PwWaterHeater(Entity):
    """Representation of a Plugwise water_heater."""

    def __init__(self, api, updater, name, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._boiler_temp = None
        self._boiler_state = False
        self._central_heating_state = False
        self._cooling_state = False
        self._domestic_hot_water_state = False
        self._central_heater_water_pressure = None
        self._unique_id = f"wh-{dev_id}-{name}"

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
        via_device = None
        dev_name = f"{self._name.split('_')[0]} Heater Central/Boiler"
        if self._dev_id is not self._api.gateway_id:
            via_device = (DOMAIN, self._api.gateway_id)
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": dev_name,
            "manufacturer": "Plugwise",
            "via_device": via_device,
        }

    @property
    def state(self):
        """Return the state of the water_heater."""
        if self._cooling_state:
            return CURRENT_HVAC_COOL
        elif (
            self._central_heating_state
            or self._boiler_state
            or self._domestic_hot_water_state
        ):
            return CURRENT_HVAC_HEAT
        else:
            return CURRENT_HVAC_IDLE

    @property
    def device_state_attributes(self):
        """Return the optional device state attributes."""
        attributes = {}
        attributes["current_operation"] = self.state
        attributes["current_temperature"] = self._boiler_temp
        attributes["water_pressure"] = self._central_heater_water_pressure
        return attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._cooling_state:
            return COOL_ICON
        elif (
            self._central_heating_state
            or self._boiler_state
            or self._domestic_hot_water_state
        ):
            return FLAME_ICON
        else:
            return IDLE_ICON

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update water_heater called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.error("Received no data for device %s.", self._name)
        else:
            if "boiler_temperature" in data:
                self._boiler_temp = data["boiler_temperature"]
            if "central_heater_water_pressure" in data:
                self._central_heater_water_pressure = data[
                    "central_heater_water_pressure"
                ]
            if "boiler_state" in data:
                if data["boiler_state"] is not None:
                    self._boiler_state = data["boiler_state"]
            if "central_heating_state" in data:
                if data["central_heating_state"] is not None:
                    self._central_heating_state = data["central_heating_state"]
            if "cooling_state" in data:
                if data["cooling_state"] is not None:
                    self._cooling_state = data["cooling_state"]
            if "domestic_hot_water_state" in data:
                self._domestic_hot_water_state = data["domestic_hot_water_state"]
