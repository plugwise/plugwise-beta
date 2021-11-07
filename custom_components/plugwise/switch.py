"""Plugwise Switch component for HomeAssistant."""
from __future__ import annotations

import logging

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (
    ATTR_ID,
    ATTR_NAME,
    ATTR_STATE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import callback

from plugwise.exceptions import PlugwiseException
from plugwise.nodes import PlugwiseNode

from .const import (
    API,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_MODEL,
    PW_TYPE,
    SMILE,
    STICK,
    USB,
    VENDOR,
)
from .gateway import SmileGateway
from .models import PW_SWITCH_TYPES, PlugwiseSwitchEntityDescription
from .usb import PlugwiseUSBEntity

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

    async def async_add_switches(mac: str):
        """Add plugwise switches."""
        entities = []
        entities.extend(
            [
                USBSwitch(api_stick.devices[mac], description)
                for description in PW_SWITCH_TYPES
                if description.plugwise_api == STICK
                and description.key in api_stick.devices[mac].features
            ]
        )
        if entities:
            async_add_entities(entities)

    for mac in hass.data[DOMAIN][config_entry.entry_id][SWITCH_DOMAIN]:
        hass.async_create_task(async_add_switches(mac))

    def discoved_device(mac: str):
        """Add switches for newly discovered device."""
        hass.async_create_task(async_add_switches(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


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
                for description in PW_SWITCH_TYPES:
                    if (
                        description.plugwise_api == SMILE
                        and description.key == data.get(ATTR_ID)
                    ):
                        entities.extend(
                            [
                                GwSwitch(
                                    api,
                                    coordinator,
                                    dev_id,
                                    coordinator.data[1][dev_id].get(ATTR_NAME),
                                    data,
                                    description,
                                )
                            ]
                        )
                        _LOGGER.debug("Add %s switch", description.key)

    if entities:
        async_add_entities(entities, True)


class GwSwitch(SmileGateway, SwitchEntity):
    """Representation of a Smile Gateway switch."""

    def __init__(
        self,
        api,
        coordinator,
        dev_id,
        name,
        sw_data,
        description: PlugwiseSwitchEntityDescription,
    ):
        """Initialise the sensor."""
        super().__init__(
            coordinator,
            dev_id,
            name,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
            description,
        )

        self._api = api
        self._attr_device_class = description.device_class
        self._attr_entity_registry_enabled_default = (
            description.entity_registry_enabled_default
        )
        self._attr_icon = description.icon
        self._attr_is_on = False
        self._attr_name = f"{name} {description.name}"
        self._attr_should_poll = self.entity_description.should_poll
        self._dev_id = dev_id
        self._members = None
        if "members" in coordinator.data[1][dev_id]:
            self._members = coordinator.data[1][dev_id].get("members")
        self._switch = description.key
        self._sw_data = sw_data

        self._attr_unique_id = f"{dev_id}-{description.key}"
        # For backwards compatibility:
        if self._switch == "relay":
            self._attr_unique_id = f"{dev_id}-plug"
            self._attr_name = name

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        _LOGGER.debug("Turn switch.%s on", self._attr_name)
        try:
            state_on = await self._api.set_switch_state(
                self._dev_id, self._members, self._switch, STATE_ON
            )
            if state_on:
                self._attr_is_on = True
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turn switch.%s off", self._attr_name)
        try:
            state_off = await self._api.set_switch_state(
                self._dev_id, self._members, self._switch, STATE_OFF
            )
            if state_off:
                self._attr_is_on = False
                self.async_write_ha_state()
        except PlugwiseException:
            _LOGGER.error("Error while communicating to device")

    @callback
    def _async_process_data(self):
        """Update the data from the Plugs."""
        self._attr_is_on = self._sw_data.get(ATTR_STATE)
        self.async_write_ha_state()


class USBSwitch(PlugwiseUSBEntity, SwitchEntity):
    """Representation of a Stick Node switch."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseSwitchEntityDescription
    ) -> None:
        """Initialize a switch entity."""
        super().__init__(node, description)

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return getattr(self._node, self.entity_description.state_request_method)

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        setattr(self._node, self.entity_description.state_request_method, False)

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        setattr(self._node, self.entity_description.state_request_method, True)
