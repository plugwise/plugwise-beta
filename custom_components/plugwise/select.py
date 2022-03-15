"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_SCHEMA_NAME,
    COORDINATOR,
    DOMAIN,
    LOGGER,
    MASTER_THERMOSTATS,
    PW_TYPE,
    SCHEDULE_ON,
    SERVICE_SELECT,
    SERVICE_SELECT_SCHEMA,
    USB,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:
        return 
    # Considered default and for earlier setups without usb/network config_flow
    return await async_setup_entry_gateway(hass, config_entry, async_add_entities)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    async_add_entities(
        PlugwiseSelectEntity(coordinator, device_id)
        for device_id, device in coordinator.data.devices.items()
        if device["class"] in MASTER_THERMOSTATS
    )

class PlugwiseSelectEntity(PlugwiseEntity, SelectEntity):
    """Represent Smile Binary Sensors."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the binary_sensor."""
        super().__init__(coordinator, device_id)
        #self._attr_entity_registry_enabled_default = (
        #    description.entity_registry_enabled_default
        #)
        self._attr_unique_id = f"{device_id}-select_schema"
        self._attr_name = (f"{self.device.get('name', '')} Select Schema").lstrip()
        self._attr_current_option = self.device.get("selected_schema")

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return self.device.get("available_schedules")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.api.set_schedule_state(
            self.device.get("location"),
            option,
            SCHEDULE_ON,
        )
        self.set_schedule_state
