"""Plugwise number component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from plugwise.nodes import PlugwiseNode

from .const import CB_NEW_NODE, DOMAIN, PW_TYPE, STICK, USB
from .models import PW_NUMBER_TYPES, PlugwiseNumberEntityDescription
from .usb import PlugwiseUSBEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:
        return await async_setup_entry_usb(hass, config_entry, async_add_entities)


async def async_setup_entry_usb(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise sensor based on config_entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_sensors(mac: str):
        """Add plugwise sensors for device."""
        entities = []
        entities.extend(
            [
                USBNumber(api_stick.devices[mac], description)
                for description in PW_NUMBER_TYPES
                if description.plugwise_api == STICK
                and description.key in api_stick.devices[mac].features
            ]
        )
        if entities:
            async_add_entities(entities)

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.NUMBER]:
        hass.async_create_task(async_add_sensors(mac))

    def discoved_device(mac: str):
        """Add number for newly discovered device."""
        hass.async_create_task(async_add_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


class USBNumber(PlugwiseUSBEntity, NumberEntity):
    """Representation of a Plugwise Number entity"""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseNumberEntityDescription
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(node, description)

    @property
    def value(self) -> float | None:
        """Return the state of the entity."""
        if (_value := getattr(self._node, self.entity_description.key)) is not None:
            return float(_value)
        return None

    def set_value(self, value: float) -> None:
        """Update the current value."""
        setattr(self._node, self.entity_description.key, int(value))
