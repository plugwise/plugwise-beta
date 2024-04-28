"""Number platform for Plugwise integration."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from plugwise import Smile

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import get_coordinator
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
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity


@dataclass(frozen=True, kw_only=True)
class PlugwiseNumberEntityDescription(NumberEntityDescription):
    """Class describing Plugwise Number entities."""

    command: Callable[[Smile, str, str, float], Awaitable[None]]
    key: NumberType


NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key=MAX_BOILER_TEMP,
        translation_key=MAX_BOILER_TEMP,
        command=lambda api, number, dev_id, value: api.set_number_setpoint(
            number, dev_id, value
        ),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=MAX_DHW_TEMP,
        translation_key=MAX_DHW_TEMP,
        command=lambda api, number, dev_id, value: api.set_number_setpoint(
            number, dev_id, value
        ),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=TEMPERATURE_OFFSET,
        translation_key=TEMPERATURE_OFFSET,
        command=lambda api, number, dev_id, value: api.set_temperature_offset(
            number, dev_id, value
        ),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Plugwise numbers from a ConfigEntry."""
    coordinator = get_coordinator(hass, entry.entry_id)

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseNumberEntity] = []
        for device_id, device in coordinator.data.devices.items():
            for description in NUMBER_TYPES:
                if description.key in device:
                    entities.append(
                        PlugwiseNumberEntity(coordinator, device_id, description)
                    )
                    LOGGER.debug(
                        "Add %s %s number", device[ATTR_NAME], description.translation_key
                    )

        async_add_entities(entities)

    entry.async_on_unload(coordinator.async_add_listener(_add_entities))

    _add_entities()


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
        self.actuator = self.device[description.key]
        self.device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_mode = NumberMode.BOX
        self._attr_native_max_value = self.device[description.key][UPPER_BOUND]
        self._attr_native_min_value = self.device[description.key][LOWER_BOUND]

        native_step = self.device[description.key][RESOLUTION]
        if description.key != TEMPERATURE_OFFSET:
            native_step = max(native_step, 0.5)
        self._attr_native_step = native_step

    @property
    def native_value(self) -> float:
        """Return the present setpoint value."""
        return self.device[self.entity_description.key]["setpoint"]

    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        await self.entity_description.command(
            self.coordinator.api, self.entity_description.key, self.device_id, value
        )
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.name, value
        )
        await self.coordinator.async_request_refresh()
