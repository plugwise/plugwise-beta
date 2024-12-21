"""Plugwise Weather platform for Home Assistant."""

from __future__ import annotations

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PlugwiseConfigEntry
from .const import (
    CONDITION,
    GATEWAY_ID,
    HUMIDITY,
    LOGGER,  # pw-betea
    TEMPERATURE,
    WEATHER,
    WIND_BEARING,
    WINDSPEED,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0  # Upstream


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise weather from a config entry."""
    coordinator = entry.runtime_data

    gateway = coordinator.data.gateway
    entities: list[PlugwiseWeatherEntity] = []
    for device_id, device in coordinator.data.devices.items():
        if device_id == gateway[GATEWAY_ID] and WEATHER in device:
            entities.append(PlugwiseWeatherEntity(coordinator, device_id))
            LOGGER.debug("Add %s weather item %s", device["name"], )
    async_add_entities(entities)


class PlugwiseWeatherEntity(PlugwiseEntity, WeatherEntity):
    """Defines a Plugwise weather-item."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.BEAUFORT

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the weather-item."""
        super().__init__(coordinator, device_id)
        self._attr_name = "home"
        self._attr_unique_id = f"{device_id}-weather"

    @property
    def condition(self) -> str:
        """Return the current condition."""
        return self.device[WEATHER][CONDITION]

    @property
    def humidity(self) -> float:
        """Return the humidity."""
        return self.device[WEATHER][HUMIDITY]

    @property
    def native_temperature(self) -> float:
        """Return the temperature."""
        return self.device[WEATHER][TEMPERATURE]

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed."""
        return self.device[WEATHER][WINDSPEED]

    @property
    def wind_bearing(self) -> float:
        """Return the wind bearing."""
        return self.device[WEATHER][WIND_BEARING]
