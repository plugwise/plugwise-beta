"""Plugwise Switch component for HomeAssistant."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise.nodes import PlugwiseNode

from .const import (  # pw-beta usb
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    LOGGER,
    SMILE,
    STICK,
    USB,
)
from .const import PW_TYPE  # pw-beta
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .models import PW_SWITCH_TYPES, PlugwiseSwitchEntityDescription
from .usb import PlugwiseUSBEntity  # pw-beta usb
from .util import plugwise_command


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:  # pw-beta usb
        return await async_setup_entry_usb(hass, config_entry, async_add_entities)
    # Considered default and for earlier setups without usb/network config_flow
    return await async_setup_entry_gateway(hass, config_entry, async_add_entities)


async def async_setup_entry_usb(hass, config_entry, async_add_entities):  # pw-beta usb
    """Set up the USB switches from a config entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_switches(mac: str):
        """Add plugwise switches."""
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


async def async_setup_entry_gateway(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    entities: list[PlugwiseSwitchEntity] = []
    for device_id, device in coordinator.data.devices.items():
        for description in PW_SWITCH_TYPES:
            if (
                "switches" not in device
                or description.key not in device["switches"]
                or description.plugwise_api != SMILE
            ):
                continue
            entities.append(PlugwiseSwitchEntity(coordinator, device_id, description))
            LOGGER.debug("Add %s switch", description.key)
    async_add_entities(entities)


class PlugwiseSwitchEntity(PlugwiseEntity, SwitchEntity):
    """Representation of a Plugwise plug."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSwitchEntityDescription,
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return self.device["switches"].get(self.entity_description.key)

    @plugwise_command
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get("members"),
            self.entity_description.key,
            "on",
        )

    @plugwise_command
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get("members"),
            self.entity_description.key,
            "off",
        )


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
