"""Number platform for Plugwise integration."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise import DeviceData, Smile

from .const import COORDINATOR  # pw-beta
from .const import DOMAIN, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

T = TypeVar("T", bound=DeviceData)


@dataclass(kw_only=True)
class PlugwiseNumberMixin(EntityDescription, Generic[T]):
    """Mixin for Plugwise number."""

    command: Callable[[Smile, str, float], Awaitable[None]]
    pw_lookup: str = "maximum_boiler_temperature"

    def pw_get_value_by_key(
        self, obj: T, value_key: str, ret: float | int = 0
    ) -> float | int:
        """Return value from Plugwise device."""
        if result := obj[self.pw_lookup].get(value_key):  # type: ignore [literal-required]
            return cast(float | int, result)
        return ret


@dataclass
class PlugwiseNumberEntityDescription(PlugwiseNumberMixin, NumberEntityDescription):
    """Describes Plugwise number entity."""

    max_value_key: str = "upper_bound"
    min_value_key: str = "lower_bound"
    step_key_value_key: str = "resolution"
    value_key: str = "setpoint"


NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key="maximum_boiler_temperature",
        translation_key="maximum_boiler_temperature",
        command=lambda api, number, value: api.set_number_setpoint(number, value),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        pw_lookup="maximum_boiler_temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key="max_dhw_temperature",
        translation_key="max_dhw_temperature",
        command=lambda api, number, value: api.set_number_setpoint(number, value),
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        pw_lookup="max_dhw_temperature",
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
            if description.key in device and "setpoint" in device[description.key]:  # type: ignore [literal-required]
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

    @property
    def native_max_value(self) -> float:
        """Return the setpoint max. value."""
        return self.entity_description.pw_get_value_by_key(
            self.device, self.entity_description.max_value_key
        )

    @property
    def native_min_value(self) -> float:
        """Return the setpoint min. value."""
        return self.entity_description.pw_get_value_by_key(
            self.device, self.entity_description.min_value_key
        )

    @property
    def native_step(self) -> float:
        """Return the setpoint step value."""
        # Fix unpractical resolution provided by Plugwise
        return max(
            self.entity_description.pw_get_value_by_key(
                self.device, self.entity_description.step_key_value_key
            ),
            0.5,
        )

    @property
    def native_value(self) -> float:
        """Return the present setpoint value."""
        return self.entity_description.pw_get_value_by_key(
            self.device, self.entity_description.value_key
        )

    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        await self.entity_description.command(
            self.coordinator.api, self.entity_description.key, value
        )
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.name, value
        )
        await self.coordinator.async_request_refresh()
