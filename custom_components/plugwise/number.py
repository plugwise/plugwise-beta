"""Number platform for Plugwise integration."""

from dataclasses import dataclass
from typing import override

from plugwise.constants import GwEntityData

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    BOILER_TEMP,
    DHW_TEMP,
    LOGGER,
    LOWER_BOUND,
    PRESET_COOLING_TEMPERATURE_KEYS,
    PRESET_TEMPERATURE_KEYS,
    RESOLUTION,
    TEMPERATURE_OFFSET,
    UPPER_BOUND,
    NumberDataType,
    NumberType,
    SetpointType,
)

# Upstream consts
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class PlugwiseNumberEntityDescription(NumberEntityDescription):
    """Class describing Plugwise Number entities."""

    key: NumberType
    data_key: NumberDataType
    value_keys: tuple[SetpointType, ...] = ("setpoint",)


# Upstream + is there a reason we didn't rename this one prefixed?
NUMBER_TYPES = (
    PlugwiseNumberEntityDescription(
        key=BOILER_TEMP,
        data_key=BOILER_TEMP,
        translation_key="maximum_boiler_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=DHW_TEMP,
        data_key=DHW_TEMP,
        translation_key="max_dhw_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseNumberEntityDescription(
        key=TEMPERATURE_OFFSET,
        data_key=TEMPERATURE_OFFSET,
        translation_key=TEMPERATURE_OFFSET,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    *(
        PlugwiseNumberEntityDescription(
            key=key,
            data_key=key,
            translation_key=key,
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            value_keys=("setpoint", "setpoint_low"),
        )
        for key in PRESET_TEMPERATURE_KEYS
    ),
    *(
        PlugwiseNumberEntityDescription(
            key=key,
            data_key=data_key,
            translation_key=key,
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            value_keys=("setpoint_high",),
        )
        for key, data_key in zip(
            PRESET_COOLING_TEMPERATURE_KEYS, PRESET_TEMPERATURE_KEYS, strict=True
        )
    ),
)


def _value_key(
    description: PlugwiseNumberEntityDescription, device: GwEntityData
) -> SetpointType | None:
    """Return the first value key of the description present in the device data."""
    ctrl = device.get(description.data_key, {})
    return next((key for key in description.value_keys if key in ctrl), None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
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
            device = coordinator.data[device_id]
            for description in NUMBER_TYPES:
                if _value_key(description, device) is not None:
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
        self.device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_mode = NumberMode.BOX
        self._data_key = description.data_key
        ctrl = self.device.get(self._data_key, {})
        self._attr_native_max_value = ctrl.get(UPPER_BOUND, 100.0)  # Upstream const
        self._attr_native_min_value = ctrl.get(LOWER_BOUND, 0.0)  # Upstream const

        native_step = ctrl.get(RESOLUTION, 0.5)  # Upstream const
        self._attr_native_step = native_step

    @property
    @override
    def native_value(self) -> float | None:
        """Return the present setpoint value."""
        ctrl = self.device.get(self._data_key, {})
        value_keys = self.entity_description.value_keys
        return next((ctrl[key] for key in value_keys if key in ctrl), None)

    @plugwise_command
    @override
    async def async_set_native_value(self, value: float) -> None:
        """Change to the new setpoint value."""
        if self._data_key in PRESET_TEMPERATURE_KEYS:
            await self.coordinator.api.set_number(
                self.device_id,
                self._data_key,
                value,
                setpoint=_value_key(self.entity_description, self.device)
                or self.entity_description.value_keys[0],
            )
        else:
            await self.coordinator.api.set_number(
                self.device_id, self.entity_description.key, value
            )
        LOGGER.debug(
            "Setting %s to %s was successful", self.entity_description.key, value
        )
