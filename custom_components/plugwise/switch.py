"""Plugwise Switch component for HomeAssistant."""

import logging

from plugwise.smileclasses import AuxDevice, Plug

from plugwise.exceptions import PlugwiseException

from homeassistant.components.switch import SwitchEntity, DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
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
    PW_CLASS,
    PW_MODEL,
    PW_TYPE,
    PW_TYPES,
    SMILE,
    STICK,
    STICK_API,
    SWITCH_CLASSES,
    USB,
    USB_AVAILABLE_ID,
    USB_CURRENT_POWER_ID,
    USB_POWER_CONSUMPTION_TODAY_ID,
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
    smile = hass.data[DOMAIN][config_entry.entry_id][SMILE]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in smile.devices:
        for key, value in smile.devices[dev_id].items():
            if key != "switches":
                continue

            for key, value in smile.devices[dev_id]["switches"].items():
                entities.append(
                    GwSwitch(
                        api,
                        coordinator,
                        smile,
                        smile.devices[dev_id][ATTR_NAME],
                        dev_id,
                        key,
                        value,
                    )
                )

    async_add_entities(entities, True)


class GwSwitch(SmileGateway, SwitchEntity):
    """Representation of a Smile Gateway switch."""

    def __init__(
        self,
        api,
        coordinator,
        smile,
        name,
        dev_id,
        switch,
        sw_data,
    ):
        """Initialise the switch."""
        super().__init__(
            coordinator,
            dev_id,
            smile,
            name,
            smile.devices[dev_id][PW_MODEL],
            smile.devices[dev_id][VENDOR],
            smile.devices[dev_id][FW],
        )

        self._auxdev = AuxDevice(api, dev_id)
        self._plug = Plug(api, dev_id)

        self._api = api
        self._device_class = sw_data[ATTR_DEVICE_CLASS]
        self._device_name = name
        self._enabled_default = sw_data[ATTR_ENABLED_DEFAULT]
        self._is_on = False
        self._members = None
        if "members" in smile.devices[dev_id]:
            self._members = smile.devices[dev_id]["members"]
        self._name = f"{name} {sw_data[ATTR_NAME]}"
        self._switch = switch
        self._sw_data = sw_data

        self._unique_id = f"{dev_id}-{switch}"
        # For backwards compatibility:
        if self._switch == "relay":
            self._unique_id = f"{dev_id}-plug"
            self._name = name

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

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
        # _LOGGER.debug("Update switch called")
        if self._smile.devices[self._dev_id][PW_CLASS] == "gateway":
            self._gateway.update_data()
        if any(dummy in self._smile.devices[self._dev_id][PW_TYPES] for dummy in SWITCH_CLASSES):
            self._plug.update_data()
        
        self._is_on = self._sw_data[ATTR_STATE]
        self.async_write_ha_state()


class USBSwitch(NodeEntity, SwitchEntity):
    """Representation of a Stick Node switch."""

    def __init__(self, node):
        """Initialize a Node entity."""
        super().__init__(node, USB_RELAY_ID)
        self.node_callbacks = (
            USB_AVAILABLE_ID,
            USB_CURRENT_POWER_ID,
            USB_POWER_CONSUMPTION_TODAY_ID,
            USB_RELAY_ID,
        )

    @property
    def current_power_w(self):
        """Return the current power usage in W."""
        current_power = getattr(self._node, STICK_API[USB_CURRENT_POWER_ID][ATTR_STATE])
        if current_power:
            return float(round(current_power, 2))
        return None

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return getattr(self._node, STICK_API[USB_RELAY_ID][ATTR_STATE])

    @property
    def today_energy_kwh(self):
        """Return the today total energy usage in kWh."""
        today_energy = getattr(
            self._node, STICK_API[USB_POWER_CONSUMPTION_TODAY_ID][ATTR_STATE]
        )
        if today_energy:
            return float(round(today_energy, 3))
        return None

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
