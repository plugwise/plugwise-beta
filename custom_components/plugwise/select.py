"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise import DeviceData, Smile
from plugwise.constants import SelectType, SelectOptionsType

from .const import (
    COORDINATOR,  # pw-beta
    DOMAIN,
    LOGGER,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


@dataclass
class PlugwiseSelectDescriptionMixin:
    """Mixin values for Plugwise Select entities."""

    command: Callable[[Smile, str, str], Awaitable[None]]


@dataclass
class PlugwiseSelectEntityDescription(
    SelectEntityDescription, PlugwiseSelectDescriptionMixin
):
    """Class describing Plugwise Number entities."""

    key: SelectType
    options_key: SelectOptionsType


SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key="select_schedule",
        translation_key="thermostat_schedule",
        icon="mdi:calendar-clock",
        command=lambda api, loc, opt: api.set_schedule_state(loc, opt, STATE_ON),
        options_key="available_schedules",
    ),
    PlugwiseSelectEntityDescription(
        key="select_regulation_mode",
        translation_key="regulation_mode",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_regulation_mode(opt),
        options_key="regulation_modes",
    ),
    PlugwiseSelectEntityDescription(
        key="select_dhw_mode",
        translation_key="dhw_mode",
        icon="mdi:shower",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_dhw_mode(opt),
        options_key="dhw_modes",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile selector from a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    entities: list[PlugwiseSelectEntity] = []
    for device_id, device in coordinator.data.devices.items():
        for description in SELECT_TYPES:
            if (options := device[description.options_key]) and len(options) > 1:
                entities.append(
                    PlugwiseSelectEntity(coordinator, device_id, description)
                )
                LOGGER.debug("Add %s %s selector", device["name"], description.name)

    async_add_entities(entities)


class PlugwiseSelectEntity(PlugwiseEntity, SelectEntity):
    """Represent Smile selector."""

    entity_description: PlugwiseSelectEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        entity_description: PlugwiseSelectEntityDescription,
    ) -> None:
        """Initialise the selector."""
        super().__init__(coordinator, device_id)
        self.entity_description = entity_description
        self._attr_unique_id = f"{device_id}-{entity_description.key}"
        self._attr_options = []
        if options := self.device[entity_description.options_key]:
            self._attr_options = options

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        return self.device[self.entity_description.key]

    async def async_select_option(self, option: str) -> None:
        """Change to the selected entity option."""
        await self.entity_description.command(
            self.coordinator.api, self.device["location"], option
        )
        LOGGER.debug(
            "Set %s to %s was successful.",
            self.entity_description.name,
            option,
        )
        await self.coordinator.async_request_refresh()
