"""Plugwise Switch component for HomeAssistant."""

import logging

from plugwise.exceptions import PlugwiseException

from homeassistant.components.switch import SwitchEntity, DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_ID,
    ATTR_NAME,
    ATTR_STATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import callback

from .gateway import SmileGateway
from .usb import NodeEntity
from .const import (
    API,
    ATTR_ENABLED_DEFAULT,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_MODEL,
    PW_TYPE,
    STICK,
    STICK_API,
    USB,
    USB_AVAILABLE_ID,
    USB_RELAY_ID,
    VENDOR,
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
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_switch(mac):
        """Add plugwise switch."""
        if USB_RELAY_ID in api_stick.devices[mac].features:
            async_add_entities([USBSwitch(api_stick.devices[mac])])

    for mac in hass.data[DOMAIN][config_entry.entry_id][SWITCH_DOMAIN]:
        hass.async_create_task(async_add_switch(mac))

    def discoved_switch(mac):
        """Add newly discovered switch."""
        hass.async_create_task(async_add_switch(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_switch, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile switches from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in coordinator.data[1]:
        for key in coordinator.data[1][dev_id]:
            if key != "switches":
                continue

            for data in coordinator.data[1][dev_id]["switches"]:
                entities.append(
                    GwSwitch(
                        api,
                        coordinator,
                        dev_id,
                        coordinator.data[1][dev_id].get(ATTR_NAME),
                        data,
                    )
                )

    async_add_entities(entities, True)


class GwSwitch(SmileGateway, SwitchEntity):
    """Representation of a Smile Gateway sensor."""

    def __init__(
        self,
        api,
        coordinator,
        dev_id,
        name,
        sw_data,
    ):
        """Initialise the sensor."""
        super().__init__(
            coordinator,
            dev_id,
            name,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
        )

        self._api = api
        self._device_class = sw_data.get(ATTR_DEVICE_CLASS)
        self._device_name = name
        self._enabled_default = sw_data.get(ATTR_ENABLED_DEFAULT)
        self._icon = None
        self._is_on = False
        self._members = None
        if "members" in coordinator.data[1][dev_id]:
            self._members = coordinator.data[1][dev_id].get("members")
        self._name = f"{name} {sw_data.get(ATTR_NAME)}"
        self._switch = sw_data.get(ATTR_ID)
        self._sw_data = sw_data

        self._unique_id = f"{dev_id}-{self._switch}"
        # For backwards compatibility:
        if self._switch == "relay":
            self._unique_id = f"{dev_id}-plug"
            self._name = name

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def icon(self):
        """Return the icon of this entity."""
        return self._icon

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on", self._name)
        try:
            state_on = await self._api.set_switch_state(
                self._dev_id, self._members, self._switch, STATE_ON
            )
            if state_on:
                self._is_on = True
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off", self._name)
        try:
            state_off = await self._api.set_switch_state(
                self._dev_id, self._members, self._switch, STATE_OFF
            )
            if state_off:
                self._is_on = False
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    @callback
    def _async_process_data(self):
        """Update the data from the Plugs."""
        self._icon = self._sw_data.get(ATTR_ICON)
        self._is_on = self._sw_data.get(ATTR_STATE)

        self.async_write_ha_state()


class USBSwitch(NodeEntity, SwitchEntity):
    """Representation of a Stick Node switch."""

    def __init__(self, node):
        """Initialize a Node entity."""
        super().__init__(node, USB_RELAY_ID)
        self.node_callbacks = (
            USB_AVAILABLE_ID,
            USB_RELAY_ID,
        )

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return getattr(self._node, STICK_API[USB_RELAY_ID][ATTR_STATE])

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        setattr(self._node, STICK_API[USB_RELAY_ID][ATTR_STATE], False)

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        setattr(self._node, STICK_API[USB_RELAY_ID][ATTR_STATE], True)

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._node.mac}-{USB_RELAY_ID}"
