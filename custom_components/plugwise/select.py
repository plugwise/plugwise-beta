"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
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
    """Mixin values for Sensibo entities."""

    command: str
    current_option: str
    options: str


@dataclass
class PlugwiseSelectEntityDescription(
    SelectEntityDescription, PlugwiseSelectDescriptionMixin
):
    """Class describing Sensibo Number entities."""


SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key="select_schedule",
        name="Set Schedule",
        icon="mdi:calendar-clock",
        command="set_schedule_state",
        current_option="selected_schedule",
        options="available_schedules",
    ),
    PlugwiseSelectEntityDescription(
        key="select_regulation_mode",
        name="Set Regulation Mode",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        command="set_regulation_mode",
        current_option="regulation_mode",
        options="regulation_modes",
        entity_registry_enabled_default=False,
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
                description.options in device
                and len(device.get(description.options, [])) > 1
            ):
                entities.append(
                    PlugwiseSelectEntity(coordinator, device_id, description)
                )
                LOGGER.debug("Add %s %s selector", device.get("name"), description.name)

    async_add_entities(entities)


class PlugwiseSelectEntity(PlugwiseEntity, SelectEntity):
    """Represent Smile selector."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSelectEntityDescription,
    ) -> None:
        """Initialise the selector."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_name = (f"{self.device.get('name', '')} {description.name}").lstrip()

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self.device.get(self.entity_description.current_option)

    @property
    def options(self) -> list[str]:
        """Return the selectable entity options."""
        return self.device.get(self.entity_description.options, [])

    async def async_select_option(self, option: str) -> None:
        """Change to the selected entity option."""
        result = await self.async_send_api_call(option, self.entity_description.command)
        if result:
            LOGGER.debug("%s to %s was successful", self.entity_description.name, option)
            await self.coordinator.async_request_refresh()
        else:
            LOGGER.error("Failed to %s to %s", self.entity_description.name, option)
