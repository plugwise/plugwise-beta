"""Plugwise Switch component for HomeAssistant."""

import logging
from typing import Dict

from homeassistant.components.switch import SwitchDevice
from homeassistant.core import callback
from Plugwise_Smile.Smile import Smile

from .const import DOMAIN, SWITCH_ICON

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if "plug" in device["types"]:
            model = "Metered Switch"
            _LOGGER.debug("Plugwise switch Dev %s", device["name"])
            devices.append(PwSwitch(api, device["name"], dev_id, model,))
            _LOGGER.info("Added switch.%s", "{}".format(device["name"]))

    async_add_entities(devices, True)


class PwSwitch(SwitchDevice):
    """Representation of a Plugwise plug."""

    def __init__(self, api, name, dev_id, model):
        """Set up the Plugwise API."""
        self._api = api
        self._model = model
        self._name = name
        self._dev_id = dev_id
        self._device_is_on = False
        self._unique_id = f"sw-{dev_id}-{self._name}"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @callback
    def _update_callback(self):
        """Call update method."""
        self.update()
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device_is_on

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        via_device = self._api.gateway_id
        if self._dev_id is via_device:
            via_device = None

        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "model": self._model,
            "via_device": via_device,
        }

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    async def turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on.", self._name)
        try:
            state_on = await self._api.set_relay_state(self._dev_id, "on")
            if state_on:
                self._device_is_on = True
                self.async_write_ha_state()
        except Smile.PlugwiseError:
            _LOGGER.error("Error while communicating to device")

    async def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off.", self._name)
        try:
            state_off = await self._api.set_relay_state(self._dev_id, "off")
            if state_off:
                self._device_is_on = False
                self.async_write_ha_state()
        except Smile.PlugwiseError:
            _LOGGER.error("Error while communicating to device")       

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

        if not data:
            _LOGGER.error("Received no data for device %s.", self._name)
        else:
            if "relay" in data:
                self._device_is_on = data["relay"]
                _LOGGER.debug("Switch is ON is %s.", self._device_is_on)
