"""Number platform for Plugwise integration."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise import ActuatorData, Smile

from .const import (
    COORDINATOR,  # pw-beta
    DOMAIN,
    LOGGER,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity


@dataclass
class PlugwiseNumberMixin:
    """Mixin values for Plugwse entities."""

    command: Callable[[Smile, str, float], Awaitable[None]]
    native_max_value_fn: Callable[[ActuatorData], float]
    native_min_value_fn: Callable[[ActuatorData], float]
    native_step_fn: Callable[[ActuatorData], float]
    native_value_fn: Callable[[ActuatorData], float]


@dataclass
class PlugwiseNumberEntityDescription(NumberEntityDescription, PlugwiseNumberMixin):
    """Class describing Plugwise Number entities."""


NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key="maximum_boiler_temperature",
        translation_key="maximum_boiler_temperature",
        command=lambda api, number, value: api.set_number_setpoint(number, value),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_max_value_fn=lambda data: data["upper_bound"],
        native_min_value_fn=lambda data: data["lower_bound"],
        native_step_fn=lambda data: data["resolution"],
        native_value_fn=lambda data: data["setpoint"],
    ),
    PlugwiseNumberEntityDescription(
        key="max_dhw_temperature",
        translation_key="max_dhw_temperature",
        command=lambda api, number, value: api.set_number_setpoint(number, value),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_max_value_fn=lambda data: data["upper_bound"],
        native_min_value_fn=lambda data: data["lower_bound"],
        native_step_fn=lambda data: data["resolution"],
        native_value_fn=lambda data: data["setpoint"],
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
        self.actuator = self.device[description.key]  # type: ignore [literal-required]
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_mode = NumberMode.BOX

    @property
    def native_max_value(self) -> float:
        """Return the setpoint max. value."""
        return self.entity_description.native_max_value_fn(self.actuator)

    @property
    def native_min_value(self) -> float:
        """Return the setpoint min. value."""
        return self.entity_description.native_min_value_fn(self.actuator)

    @property
    def native_step(self) -> float:
        """Return the setpoint step value."""
        return max(self.entity_description.native_step_fn(self.actuator), 0.5)

    @property
    def native_value(self) -> float:
        """Return the present setpoint value."""
        return self.entity_description.native_value_fn(self.actuator)

    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        await self.entity_description.command(
            self.coordinator.api, self.entity_description.key, value
        )
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.name, value
        )
        await self.coordinator.async_request_refresh()
