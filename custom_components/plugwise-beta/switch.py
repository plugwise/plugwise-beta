"""Plugwise Water Heater component for HomeAssistant."""

import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from Plugwise_Smile.Smile import Smile

from .const import DOMAIN, SWITCH_ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if "plug" in device["types"]:
            data = api.get_device_data(dev_id)
            # _LOGGER.debug(data)
            _LOGGER.info("Plugwise switch Dev %s", device["name"])
            switch = PwSwitch(api, updater, device["name"], dev_id)
            devices.append(switch)
            _LOGGER.info("Added switch.%s", "{}".format(device["name"]))

    async_add_entities(devices, True)


class PwSwitch(SwitchDevice):
    """Representation of a Plugwise plug."""

    def __init__(self, api, updater, name, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._device_is_on = False
        self._unique_id = f"{dev_id}-plug"

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
    def is_on(self):
        """Return true if device is on."""
        return self._device_is_on

    async def turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on.", self._name)
        await self._api.set_relay_state(self._dev_id, "on")
        await self._updater.async_refresh_all()

    async def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off.", self._name)
        await self._api.set_relay_state(self._dev_id, "off")
        await self._updater.async_refresh_all()

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return SWITCH_ICON

    def update(self):
        """Update the data from the Plugs."""
        _LOGGER.debug("Update switch called")

        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            if "relay" in data:
                self._device_is_on = data["relay"] == "on"
                _LOGGER.debug("Switch is ON is %s.", self._device_is_on)
