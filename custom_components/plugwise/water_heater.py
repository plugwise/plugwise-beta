"""Plugwise water heater component for HomeAssistant."""

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import ATTR_NAME, STATE_OFF, STATE_ON, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    BINARY_SENSORS,
    DEV_CLASS,
    LOGGER,
    LOWER_BOUND,
    SENSORS,
    TARGET_TEMP,
    UPPER_BOUND,
)
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

MODE_HEAT = "heat"
MODE_OFF = "off"
OPERATION_MODES = [MODE_HEAT, MODE_OFF]


async def async_setup_entry(
    hass: HomeAssistant,
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
            if device[DEV_CLASS] == "heater_central" and device.get(BINARY_SENSORS, {}).get("dhw_state") is not None:
                entities.append(PlugwiseWaterHeaterEntity(coordinator, device_id))
                LOGGER.debug("Add %s water_heater", device[ATTR_NAME])
        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseWaterHeaterEntity(PlugwiseEntity, WaterHeaterEntity):
    """Representation of a Plugwise water heater."""

    _attr_name = None
    _attr_operation_list = OPERATION_MODES
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the water_heater."""
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}-water_heater"

        self._attr_max_temp = self.device.get("max_dhw_temperature", {}).get(UPPER_BOUND, 75.0)
        self._attr_min_temp = self.device.get("max_dhw_temperature", {}).get(LOWER_BOUND, 40.0)
        self._attr_supported_features = WaterHeaterEntityFeature.OPERATION_MODE
        if self.device.get("max_dhw_temperature"):
            self._attr_supported_features |= WaterHeaterEntityFeature.TARGET_TEMPERATURE

    @property
    def current_operation(self) -> str | None:
        """Return current readable operation mode."""
        if (state := self.device.get(BINARY_SENSORS, {}).get("dhw_state")) is not None:
            if state:
                return STATE_ON
            return STATE_OFF
        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature."""
        return self.device.get(SENSORS, {}).get("water_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the water temperature we try to reach."""
        return self.device.get("max_dhw_temperature", {}).get(TARGET_TEMP)
