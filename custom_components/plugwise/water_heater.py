"""Plugwise water heater component for HomeAssistant."""

from typing import Any, override

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import (
    ATTR_NAME,
    ATTR_TEMPERATURE,
    STATE_OFF,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DHW_MODE, DHW_MODES, DHW_TEMP, LOGGER, LOWER_BOUND, UPPER_BOUND
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Plugwise water_heater from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseWaterHeaterEntity] = []
        for device_id in coordinator.new_devices:
            device = coordinator.data[device_id]
            if device.get(DHW_TEMP) is not None:
                entities.append(PlugwiseWaterHeaterEntity(coordinator, device_id))
                LOGGER.debug("Add %s water_heater", device[ATTR_NAME])
        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseWaterHeaterEntity(PlugwiseEntity, WaterHeaterEntity):
    """Representation of a Plugwise water heater."""

    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the water_heater."""
        super().__init__(coordinator, device_id)

        entity_name = f"{self.device[ATTR_NAME]}".lower()
        self._attr_unique_id = f"{device_id}-{entity_name}"

        self.dhw_temp = self.device.get(DHW_TEMP, {})
        if self.dhw_temp:
            self._attr_max_temp = self.dhw_temp.get(UPPER_BOUND, 75.0)
            self._attr_min_temp = self.dhw_temp.get(LOWER_BOUND, 40.0)
        self._attr_supported_features = WaterHeaterEntityFeature.OPERATION_MODE
        self._attr_supported_features |= WaterHeaterEntityFeature.TARGET_TEMPERATURE


    @property
    @override
    def current_operation(self) -> str | None:
        """Return current readable operation mode."""
        return self.device.get(DHW_MODE)

    @property
    @override
    def current_temperature(self) -> float | None:
        """Return the current water temperature."""
        return self.dhw_temp.get("current")

    @property
    @override
    def operation_list(self) -> list[str]:
        """Return the list of available operation modes."""
        if (op_list := self.device.get(DHW_MODES, [])):
            return op_list
        return [STATE_OFF]  # pragma: no cover

    @property
    @override
    def target_temperature(self) -> float | None:
        """Return the water temperature we try to reach."""
        return self.dhw_temp.get("setpoint")

    @plugwise_command
    @override
    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the operation mode."""
        list_type: int = len(self.operation_list)
        await self.coordinator.api.set_dhw_mode(DHW_MODE, self._dev_id, list_type, operation_mode)

    @plugwise_command
    @override
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.api.set_number(self._dev_id, DHW_TEMP, float(temperature))
