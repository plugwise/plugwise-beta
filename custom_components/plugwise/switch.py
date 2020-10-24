"""Plugwise Switch component for HomeAssistant."""

import logging

from plugwise.smile import Smile
from plugwise.exceptions import PlugwiseException

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback

from .gateway import SmileGateway
from .usb import NodeEntity
from .const import (
    API,
    ATTR_ENABLED_DEFAULT,
    AVAILABLE_SENSOR_ID,
    CB_NEW_NODE,
    COORDINATOR,
    CURRENT_POWER_SENSOR_ID,
    DOMAIN,
    PW_TYPE,
    SENSORS,
    STICK,
    SWITCH_CLASSES,
    SWITCH_ICON,
    SWITCHES,
    TODAY_ENERGY_SENSOR_ID,
    USB,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:
        return await async_setup_entry_usb(hass, config_entry, async_add_entities)
    # Considered default and for earlier setups without usb/network config_flow
    return await async_setup_entry_gateway(hass, config_entry, async_add_entities)


async def async_setup_entry_usb(hass, config_entry, async_add_entities):
    """Set up the USB switches from a config entry."""
    stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_switch(mac):
        """Add plugwise switch."""
        node = stick.node(mac)
        for switch_type in node.get_switches():
            if switch_type in SWITCHES:
                async_add_entities([USBSwitch(node, mac, switch_type)])

    for mac in hass.data[DOMAIN][config_entry.entry_id]["switch"]:
        hass.async_create_task(async_add_switch(mac))

    def discoved_switch(mac):
        """Add newly discovered switch."""
        hass.async_create_task(async_add_switch(mac))

    # Listen for discovered nodes
    stick.subscribe_stick_callback(discoved_switch, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    all_devices = api.get_all_devices()
    for dev_id, device_properties in all_devices.items():
        members = None
        model = None
        if any(dummy in device_properties["types"] for dummy in SWITCH_CLASSES):
            if "plug" in device_properties["types"]:
                model = "Metered Switch"
            if "switch_group" in device_properties["types"]:
                members = device_properties["members"]
                model = "Switch Group"
            _LOGGER.debug("Plugwise switch Dev %s", device_properties["name"])
            entities.append(
                GwSwitch(
                    api, coordinator, device_properties["name"], dev_id, members, model,
                )
            )
            _LOGGER.info("Added switch.%s", "{}".format(device_properties["name"]))

    async_add_entities(entities, True)


class GwSwitch(SmileGateway, SwitchEntity):
    """Representation of a Plugwise plug."""

    def __init__(self, api, coordinator, name, dev_id, members, model):
        """Set up the Plugwise API."""
        self._enabled_default = True

        super().__init__(api, coordinator, name, dev_id)

        self._members = members
        self._model = model

        self._is_on = False

        self._unique_id = f"{dev_id}-plug"

    @property
    def icon(self):
        """Return the icon of the entity."""
        return SWITCH_ICON

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on.", self._name)
        try:
            state_on = await self._api.set_relay_state(
                self._dev_id, self._members, STATE_ON
            )
            if state_on:
                self._is_on = True
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off.", self._name)
        try:
            state_off = await self._api.set_relay_state(
                self._dev_id, self._members, STATE_OFF
            )
            if state_off:
                self._is_on = False
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    @callback
    def _async_process_data(self):
        """Update the data from the Plugs."""
        _LOGGER.debug("Update switch called")

        data = self._api.get_device_data(self._dev_id)

        if "relay" not in data:
            self.async_write_ha_state()
            return

        self._is_on = data["relay"]
        _LOGGER.debug("Switch is ON is %s.", self._is_on)

        self.async_write_ha_state()


class USBSwitch(NodeEntity, SwitchEntity):
    """Representation of a switch."""

    def __init__(self, node, mac, switch_id):
        """Initialize a Node entity."""
        super().__init__(node, mac)
        self.switch_id = switch_id
        self.switch_type = SWITCHES[self.switch_id]
        if (CURRENT_POWER_SENSOR_ID in node.get_sensors()) and (
            TODAY_ENERGY_SENSOR_ID in node.get_sensors()
        ):
            self.node_callbacks = (
                AVAILABLE_SENSOR_ID,
                switch_id,
                CURRENT_POWER_SENSOR_ID,
                TODAY_ENERGY_SENSOR_ID,
            )
        else:
            self.node_callbacks = (AVAILABLE_SENSOR_ID, self.switch_id)

    @property
    def current_power_w(self):
        """Return the current power usage in W."""
        current_power = getattr(self._node, SENSORS[CURRENT_POWER_SENSOR_ID]["state"])()
        if current_power:
            return float(round(current_power, 2))
        return None

    @property
    def device_class(self):
        """Return the device class of this switch."""
        return self.switch_type["class"]

    @property
    def entity_registry_enabled_default(self):
        """Return the switch registration state."""
        return self.switch_type[ATTR_ENABLED_DEFAULT]

    @property
    def icon(self):
        """Return the icon."""
        return None if self.switch_type["class"] else self.switch_type["icon"]

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return getattr(self._node, self.switch_type["state"])()

    @property
    def today_energy_kwh(self):
        """Return the today total energy usage in kWh."""
        today_energy = getattr(self._node, SENSORS[TODAY_ENERGY_SENSOR_ID]["state"])()
        if today_energy:
            return float(round(today_energy, 3))
        return None

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        getattr(self._node, self.switch_type["switch"])(False)

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        getattr(self._node, self.switch_type["switch"])(True)

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._mac}-{self.switch_id}"
