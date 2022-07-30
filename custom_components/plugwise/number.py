"""Number platform for Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR, DOMAIN, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity


@dataclass
class PlugwiseNumberEntityDescription(NumberEntityDescription):
    """Class describing Plugwise Number entities."""


NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key="maximum_boiler_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        name="Maximum boiler temperature setpoint",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key="domestic_hot_water_setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        name="Domestic hot water setpoint",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise number platform."""

    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    entities: list[PlugwiseNumberEntity] = []
    for device_id, device in coordinator.data.devices.items():
        for description in NUMBER_TYPES:
            if description.key in device:
                entities.append(
                    PlugwiseNumberEntity(coordinator, device_id, description)
                )
                LOGGER.debug("Add %s %s number", device["name"], description.name)

    async_add_entities(entities)


class PlugwiseNumberEntity(PlugwiseEntity, NumberEntity):
    """Representation of a Plugwise number."""

    entity_description: PlugwiseNumberEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseNumberEntityDescription,
    ) -> None:
        """Initiate Plugwise Number."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_mode = NumberMode.BOX
        self._item = description.key

    @property
    def native_step(self) -> float:
        """Return the setpoint step value."""
        return max(self.device[self._item]["resolution"], 1)

    @property
    def native_value(self) -> float:
        """Return the present setpoint value."""
        return self.device[self._item]["setpoint"]

    @property
    def native_min_value(self) -> float:
        """Return the setpoint min. value."""
        return self.device[self._item]["lower_bound"]

    @property
    def native_max_value(self) -> float:
        """Return the setpoint max. value."""
        return self.device[self._item]["upper_bound"]

    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        await self.coordinator.api.set_number_setpoint(self._item, value),
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.name, value
        )
        await self.coordinator.async_request_refresh()
