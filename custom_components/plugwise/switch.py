"""Plugwise Switch component for HomeAssistant."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from plugwise.constants import SwitchType

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COOLING_ENA_SWITCH,
    COORDINATOR,  # pw-beta
    DHW_CM_SWITCH,
    DOMAIN,
    LOCK,
    LOGGER,
    MEMBERS,
    RELAY,
    SWITCHES,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command


@dataclass(frozen=True)
class PlugwiseSwitchEntityDescription(SwitchEntityDescription):
    """Describes Plugwise switch entity."""

    key: SwitchType


PLUGWISE_SWITCHES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=DHW_CM_SWITCH,
        translation_key=DHW_CM_SWITCH,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=LOCK,
        translation_key=LOCK,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=RELAY,
        translation_key=RELAY,
        device_class=SwitchDeviceClass.SWITCH,
    ),
    PlugwiseSwitchEntityDescription(
        key=COOLING_ENA_SWITCH,
        translation_key=COOLING_ENA_SWITCH,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[PlugwiseSwitchEntity] = []
    for device_id, device in coordinator.data.devices.items():
        if not (switches := device.get(SWITCHES)):
            continue
        for description in PLUGWISE_SWITCHES:
            if description.key not in switches:
                continue
            entities.append(PlugwiseSwitchEntity(coordinator, device_id, description))
            LOGGER.debug(
                "Add %s %s switch", device[ATTR_NAME], description.translation_key
            )

    async_add_entities(entities)


class PlugwiseSwitchEntity(PlugwiseEntity, SwitchEntity):
    """Representation of a Plugwise plug."""

    entity_description: PlugwiseSwitchEntityDescription

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
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.device[SWITCHES][self.entity_description.key]

    @plugwise_command
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get(MEMBERS),
            self.entity_description.key,
            "on",
        )

    @plugwise_command
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get(MEMBERS),
            self.entity_description.key,
            "off",
        )
