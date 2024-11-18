"""Number platform for Plugwise integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PlugwiseConfigEntry
from .const import (
    LOGGER,
    LOWER_BOUND,
    MAX_BOILER_TEMP,
    MAX_DHW_TEMP,
    RESOLUTION,
    TEMPERATURE_OFFSET,
    UPPER_BOUND,
    NumberType,
)

# Upstream consts
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0  # Upstream


@dataclass(frozen=True, kw_only=True)
class PlugwiseNumberEntityDescription(NumberEntityDescription):
    """Class describing Plugwise Number entities."""

    key: NumberType


# Upstream + is there a reason we didn't rename this one prefixed?
NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key=MAX_BOILER_TEMP,
        translation_key=MAX_BOILER_TEMP,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=MAX_DHW_TEMP,
        translation_key=MAX_DHW_TEMP,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=TEMPERATURE_OFFSET,
        translation_key=TEMPERATURE_OFFSET,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise number platform from a config entry."""
    # Upstream above to adhere to standard used
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        # Upstream consts
        # async_add_entities(
        #     PlugwiseNumberEntity(coordinator, device_id, description)
        #     for device_id in coordinator.new_devices
        #     for description in NUMBER_TYPES
        #     if description.key in coordinator.data.devices[device_id]
        # )

        # pw-beta alternative for debugging
        entities: list[PlugwiseNumberEntity] = []
        for device_id in coordinator.new_devices:
            device = coordinator.data.devices[device_id]
            for description in NUMBER_TYPES:
                if description.key in device:
                    entities.append(
                        PlugwiseNumberEntity(coordinator, device_id, description)
                    )
                    LOGGER.debug(
                        "Add %s %s number", device["name"], description.translation_key
                    )

        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


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
        self.actuator = self.device_or_zone[description.key]  # Upstream
        self.device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_mode = NumberMode.BOX
        self._attr_native_max_value = self.device_or_zone[description.key][UPPER_BOUND]  # Upstream const
        self._attr_native_min_value = self.device_or_zone[description.key][LOWER_BOUND]  # Upstream const

        native_step = self.device_or_zone[description.key][RESOLUTION]  # Upstream const
        if description.key != TEMPERATURE_OFFSET:  # Upstream const
            native_step = max(native_step, 0.5)
        self._attr_native_step = native_step

    @property
    def native_value(self) -> float:
        """Return the present setpoint value."""
        return self.device_or_zone[self.entity_description.key]["setpoint"]

    @plugwise_command
    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        await self.coordinator.api.set_number(self.device_id, self.entity_description.key, value)
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.key, value
        )
