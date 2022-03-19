"""Plugwise Select component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COORDINATOR,
    DOMAIN,
    MASTER_THERMOSTATS,
    LOGGER,
    SCHEDULE_ON,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile selector from a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    entities: list[ScheduleSelectEntity | RegulationSelectEntity] = []
    for device_id, device in coordinator.data.devices.items():
        if device["class"] in MASTER_THERMOSTATS and len(device.get("available_schedules")) > 1:
            entities.extend([ScheduleSelectEntity(coordinator, device_id)])
            LOGGER.debug("Add %s Schedule selector", device.get("name"))

        if device["class"] == "gateway" and "regulation_modes" in device and len(device.get("regulation_modes")) > 1:
            entities.extend([RegulationSelectEntity(coordinator, device_id)])
            LOGGER.debug("Add %s Regulation Mode selector", device.get("name"))

    async_add_entities(entities)


class ScheduleSelectEntity(PlugwiseEntity, SelectEntity):
    """Represent Smile selector."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the selector."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}-select_schedule"
        self._attr_name = (f"{self.device.get('name', '')} Select Schedule").lstrip()
        self._attr_options = self.device.get("available_schedules", [])

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = self.device.get("selected_schedule")
        if value is None or value not in self._attr_options:
            return None

        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.api.set_schedule_state(
            self.device.get("location"),
            option,
            SCHEDULE_ON,
        )
        await self.coordinator.async_request_refresh()


class RegulationSelectEntity(PlugwiseEntity, SelectEntity):
    """Represent Smile selector."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the selector."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}-select_regulation_mode"
        self._attr_name = (
            f"{self.device.get('name', '')} Select Regulation Mode"
        ).lstrip()
        self._attr_options = self.device.get("regulation_modes", [])

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = self.device.get("regulation_mode")
        if value is None or value not in self._attr_options:
            return None

        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.api.set_regulation_mode(option)
        await self.coordinator.async_request_refresh()
