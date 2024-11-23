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
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PlugwiseConfigEntry
from .const import (
    COOLING_ENA_SWITCH,
    DHW_CM_SWITCH,
    LOCK,
    LOGGER,  # pw-beta
    MEMBERS,
    RELAY,
    SWITCHES,
)

# Upstream consts
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0  # Upstream


@dataclass(frozen=True)
class PlugwiseSwitchEntityDescription(SwitchEntityDescription):
    """Describes Plugwise switch entity."""

    key: SwitchType


# Upstream consts
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
    entry: PlugwiseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise switches from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_pw_entities:
            return

        # Upstream consts
        # async_add_entities(
        #     PlugwiseSwitchEntity(coordinator, pw_entity_id, description)
        #     for pw_entity_id in coordinator.new_pw_entities
        #     if (switches := coordinator.data.entities[pw_entity_id].get(SWITCHES))
        #     for description in PLUGWISE_SWITCHES
        #     if description.key in switches
        # )
        # pw-beta alternative for debugging
        entities: list[PlugwiseSwitchEntity] = []
        for pw_entity_id in coordinator.new_pw_entities:
            pw_entity = coordinator.data.entities[pw_entity_id]
            if not (switches := pw_entity.get(SWITCHES)):
                continue
            for description in PLUGWISE_SWITCHES:
                if description.key not in switches:
                    continue
                entities.append(PlugwiseSwitchEntity(coordinator, pw_entity_id, description))
                LOGGER.debug(
                    "Add %s %s switch", pw_entity["name"], description.translation_key
                )
        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseSwitchEntity(PlugwiseEntity, SwitchEntity):
    """Representation of a Plugwise plug."""

    entity_description: PlugwiseSwitchEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        pw_entity_id: str,
        description: PlugwiseSwitchEntityDescription,
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, pw_entity_id)
        self.entity_description = description
        self._attr_unique_id = f"{pw_entity_id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.pw_entity[SWITCHES][self.entity_description.key]  # Upstream const

    @plugwise_command
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.coordinator.api.set_switch_state(
            self._pw_ent_id,
            self.pw_entity.get(MEMBERS),
            self.entity_description.key,
            "on",
        )  # Upstream const

    @plugwise_command
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.coordinator.api.set_switch_state(
            self._pw_ent_id,
            self.pw_entity.get(MEMBERS),
            self.entity_description.key,
            "off",
        )  # Upstream const
