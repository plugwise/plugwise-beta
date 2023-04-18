"""Plugwise USB Switch component for HomeAssistant."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise_usb.nodes import PlugwiseNode

from . import PlugwiseUSBEntity  # pw-beta usb
from .const import CB_NEW_NODE, DOMAIN, STICK
from .models import PW_SWITCH_TYPES, PlugwiseSwitchEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the USB switches from a config entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_switches(mac: str):
        """Add Plugwise USB switches."""
        entities: list[USBSwitch] = []
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

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.SWITCH]:
        hass.async_create_task(async_add_switches(mac))

    def discoved_device(mac: str):
        """Add switches for newly discovered device."""
        hass.async_create_task(async_add_switches(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


# Github issue #265
class USBSwitch(PlugwiseUSBEntity, SwitchEntity):  # type: ignore[misc]  # pw-beta usb
    """Representation of a Stick Node switch."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseSwitchEntityDescription
    ) -> None:
        """Initialize a switch entity."""
        super().__init__(node, description)

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        # Github issue #265
        return getattr(self._node, self.entity_description.state_request_method)  # type: ignore[attr-defined]

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        setattr(self._node, self.entity_description.state_request_method, False)

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        setattr(self._node, self.entity_description.state_request_method, True)
