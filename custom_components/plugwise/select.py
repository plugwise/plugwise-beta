"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise import DeviceData, Smile

from .const import COORDINATOR  # pw-beta
from .const import DOMAIN, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0

T = TypeVar("T", bound=DeviceData)


@dataclass(kw_only=True)
class PlugwiseSelectMixin(EntityDescription, Generic[T]):
    """Mixin for Plugwise select."""

    command: Callable[[Smile, str, str], Awaitable[Any]]
    pw_key: str = "selected_schedule"
    pw_list_key: str = "available_schedules"

    def pw_get_value(self, obj: T, ret: str = "") -> str:
        """Return value from Plugwise device."""
        if result := obj.get(self.pw_key):
            return cast(str, result)
        if result := obj.get(self.key):
            return cast(str, result)
        return ret

    def pw_get_values(self, obj: T, ret: list[str] = []) -> list[str]:
        """Return list of values from Plugwise device."""
        if result := obj.get(self.pw_list_key):
            return cast(list[str], result)
        if result := obj.get(self.key):
            return cast(list[str], result)
        return ret


@dataclass
class PlugwiseSelectEntityDescription(PlugwiseSelectMixin, SelectEntityDescription):
    """Describes Plugwise select entity."""


SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key="select_schedule",
        translation_key="thermostat_schedule",
        icon="mdi:calendar-clock",
        command=lambda api, loc, opt: api.set_schedule_state(loc, opt, STATE_ON),
        pw_key="selected_schedule",
        pw_list_key="available_schedules",
    ),
    PlugwiseSelectEntityDescription(
        key="select_regulation_mode",
        translation_key="regulation_mode",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_regulation_mode(opt),
        pw_key="regulation_mode",
        pw_list_key="regulation_modes",
    ),
    PlugwiseSelectEntityDescription(
        key="select_dhw_mode",
        translation_key="dhw_mode",
        icon="mdi:shower",
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_dhw_mode(opt),
        pw_key="dhw_mode",
        pw_list_key="dhw_modes",
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
                description.pw_list_key in device
                and len(device[description.pw_list_key]) > 1  # type: ignore [literal-required]
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
        return self.entity_description.pw_get_value(self.device)

    @property
    def options(self) -> list[str]:
        """Return the selectable entity options."""
        return self.entity_description.pw_get_values(self.device)

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
