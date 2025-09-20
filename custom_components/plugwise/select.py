"""Plugwise Select component for Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import STATE_ON, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

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

# Upstream consts
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class PlugwiseSelectEntityDescription(SelectEntityDescription):
    """Class describing Plugwise Select entities."""

    key: SelectType
    options_key: SelectOptionsType


# Upstream + is there a reason we didn't rename this one prefixed?
SELECT_TYPES = (
    PlugwiseSelectEntityDescription(
        key=SELECT_SCHEDULE,
        translation_key=SELECT_SCHEDULE,
        options_key=AVAILABLE_SCHEDULES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_REGULATION_MODE,
        translation_key=REGULATION_MODE,
        entity_category=EntityCategory.CONFIG,
        options_key=REGULATION_MODES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_DHW_MODE,
        translation_key=DHW_MODE,
        entity_category=EntityCategory.CONFIG,
        options_key=DHW_MODES,
    ),
    PlugwiseSelectEntityDescription(
        key=SELECT_GATEWAY_MODE,
        translation_key=GATEWAY_MODE,
        entity_category=EntityCategory.CONFIG,
        options_key=GATEWAY_MODES,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Plugwise selector from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        # Upstream consts
        # async_add_entities(
        #     PlugwiseSelectEntity(coordinator, device_id, description)
        #     for device_id in coordinator.new_devices
        #     for description in SELECT_TYPES
        #     if description.options_key in coordinator.data.devices[device_id]
        # )
        # pw-beta alternative for debugging
        entities: list[PlugwiseSelectEntity] = []
        for device_id in coordinator.new_devices:
            device = coordinator.data[device_id]
            for description in SELECT_TYPES:
                if device.get(description.options_key):
                    entities.append(
                        PlugwiseSelectEntity(coordinator, device_id, description)
                    )
                    LOGGER.debug(
                        "Add %s %s selector", device["name"], description.translation_key
                    )

        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


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
        self._attr_unique_id = f"{device_id}-{entity_description.key}"
        self.entity_description = entity_description

        self._location = device_id
        if (location := self.device.get(LOCATION)) is not None:
            self._location = location

    @property
    def current_option(self) -> str| None:
        """Return the selected entity option to represent the entity state."""
        return self.device.get(self.entity_description.key)

    @property
    def options(self) -> list[str]:
        """Return the available select-options."""
        if options := self.device.get(self.entity_description.options_key) is not None:
            return options
        return []

    @plugwise_command
    async def async_select_option(self, option: str) -> None:
        """Change to the selected entity option.

        Location ID and STATE_ON are required for the thermostat-schedule select.
        """
        await self.coordinator.api.set_select(
            self.entity_description.key, self._location, option, STATE_ON
        )
        LOGGER.debug(
            "Set %s to %s was successful",
            self.entity_description.key,
            option,
        )
