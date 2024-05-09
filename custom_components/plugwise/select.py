"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from plugwise import Smile

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AVAILABLE_SCHEDULES,
    DHW_MODE,
    DHW_MODES,
    GATEWAY_MODE,
    GATEWAY_MODES,
    LOCATION,
    LOGGER,
    REGULATION_MODE,
    REGULATION_MODES,
    SELECT_DHW_MODE,
    SELECT_GATEWAY_MODE,
    SELECT_REGULATION_MODE,
    SELECT_SCHEDULE,
    SelectOptionsType,
    SelectType,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity, get_coordinator

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class PlugwiseSelectEntityDescription(SelectEntityDescription):
    """Class describing Plugwise Select entities."""

    command: Callable[[Smile, str, str], Awaitable[None]]
    key: SelectType
    options_key: SelectOptionsType


SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key=SELECT_SCHEDULE,
        translation_key=SELECT_SCHEDULE,
        command=lambda api, loc, opt: api.set_schedule_state(loc, STATE_ON, opt),
        options_key=AVAILABLE_SCHEDULES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_REGULATION_MODE,
        translation_key=REGULATION_MODE,
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_regulation_mode(opt),
        options_key=REGULATION_MODES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_DHW_MODE,
        translation_key=DHW_MODE,
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_dhw_mode(opt),
        options_key=DHW_MODES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_GATEWAY_MODE,
        translation_key=GATEWAY_MODE,
        entity_category=EntityCategory.CONFIG,
        command=lambda api, loc, opt: api.set_gateway_mode(opt),
        options_key=GATEWAY_MODES,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile selector from a ConfigEntry."""
    coordinator = get_coordinator(hass, entry.entry_id)

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseSelectEntity] = []
        for device_id, device in coordinator.data.devices.items():
            for description in SELECT_TYPES:
                if description.options_key in device:
                    entities.append(
                        PlugwiseSelectEntity(coordinator, device_id, description)
                    )
                    LOGGER.debug(
                        "Add %s %s selector", device[ATTR_NAME], description.translation_key
                    )

        async_add_entities(entities)

    entry.async_on_unload(coordinator.async_add_listener(_add_entities))

    _add_entities()


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
        self._attr_options = self.device[entity_description.options_key]

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        return self.device[self.entity_description.key]

    async def async_select_option(self, option: str) -> None:
        """Change to the selected entity option."""
        await self.entity_description.command(
            self.coordinator.api, self.device[LOCATION], option
        )
        LOGGER.debug(
            "Set %s to %s was successful.",
            self.entity_description.name,
            option,
        )
        await self.coordinator.async_request_refresh()
