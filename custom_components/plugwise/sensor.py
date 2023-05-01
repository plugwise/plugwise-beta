"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR  # pw-beta
from .const import DOMAIN, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .models import PW_SENSOR_TYPES, PlugwiseSensorEntityDescription

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[PlugwiseSensorEntity] = []
    for device_id, device in coordinator.data.devices.items():
        for description in PW_SENSOR_TYPES:
            if (
                "sensors" not in device
                or device["sensors"].get(description.key) is None
            ):
                continue

            entities.append(
                PlugwiseSensorEntity(
                    coordinator,
                    device_id,
                    description,
                )
            )
            LOGGER.debug("Add %s sensor", description.key)

    async_add_entities(entities)


class PlugwiseSensorEntity(PlugwiseEntity, SensorEntity):
    """Represent Plugwise Sensors."""

    entity_description: PlugwiseSensorEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def native_value(self) -> int | float:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self.device)
