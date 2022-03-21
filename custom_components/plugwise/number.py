"""Number platform for Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR, DOMAIN, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity


@dataclass
class PlugwiseEntityDescriptionMixin:
    """Mixin values for Plugwse entities."""

    command: str


@dataclass
class PlugwiseNumberEntityDescription(
    NumberEntityDescription, PlugwiseEntityDescriptionMixin
):
    """Class describing Plugwise Number entities."""


NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key="maximum_boiler_temperature",
        command="set_max_boiler_temperature",
        name="Maximum Boiler Temperature Setpoint",
        icon="mdi:thermometer",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        min_value=25,
        max_value=95,
        step=5,
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
                LOGGER.debug("Add %s %s number", device.get("name"), description.name)

    async_add_entities(entities)


class PlugwiseNumberEntity(PlugwiseEntity, NumberEntity):
    """Representation of a Plugwise number."""

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
        self._attr_name = (f"{self.device.get('name', '')} {description.name}").lstrip()

    @property
    def value(self) -> float | None:
        """Return the present setpoint value."""
        return self.device.get(self.entity_description.key)

    async def async_set_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        result = await self.async_send_api_call(value, self.entity_description.command)
        if result:
            LOGGER.debug("Setting %s to %s was successful", self.entity_description.name, value)
            await self.coordinator.async_request_refresh()
        else:
            raise HomeAssistantError("Failed to set %s", self.entity_description.name)
