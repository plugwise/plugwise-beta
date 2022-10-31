"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from plugwise import Smile

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COORDINATOR,
    DOMAIN,
    LOGGER,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


@dataclass
class PlugwiseSelectDescriptionMixin:
    """Mixin values for Plugwise Select entities."""

    command: Callable[[Smile, str, str], Awaitable[Any]]
    current_option_key: str
    options_key: str


@dataclass
class PlugwiseSelectEntityDescription(
    SelectEntityDescription, PlugwiseSelectDescriptionMixin
):
    """Class describing Plugwise Number entities."""


SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key="select_schedule",
        name="Thermostat schedule",
        icon="mdi:calendar-clock",
        command=lambda api, loc, opt: api.set_schedule_state(loc, opt, STATE_ON),
        current_option_key="selected_schedule",
        options_key="available_schedules",
    ),
    PlugwiseSelectEntityDescription(
        key="select_regulation_mode",
        name="Regulation mode",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_regulation_mode(opt),
        current_option_key="regulation_mode",
        options_key="regulation_modes",
        device_class="plugwise__regulation_mode",
    ),
    PlugwiseSelectEntityDescription(
        key="select_dhw_mode",
        name="DHW mode",
        icon="mdi:shower",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_dhw_mode(opt),
        current_option_key="dhw_mode",
        options_key="dhw_modes",
        device_class="plugwise__dhw_mode",
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
            if (
                description.options_key in device
                and len(device[description.options_key]) > 1  # typing: ignore[literal-required]
            ):
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

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        return self.device[self.entity_description.current_option_key]  # typing: ignore[literal-required]

    @property
    def options(self) -> list[str]:
        """Return the selectable entity options."""
        return self.device[self.entity_description.options_key]  # typing: ignore[literal-required]

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
