"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from plugwise.nodes import PlugwiseNode

from .const import (
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    LOGGER,
    PW_TYPE,
    STICK,
    USB,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .models import PW_SENSOR_TYPES, PlugwiseSensorEntityDescription
from .usb import PlugwiseUSBEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:
        return await async_setup_entry_usb(hass, config_entry, async_add_entities)
    # Considered default and for earlier setups without usb/network config_flow
    return await async_setup_entry_gateway(hass, config_entry, async_add_entities)


async def async_setup_entry_usb(hass, config_entry, async_add_entities):
    """Set up Plugwise sensor based on config_entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_sensors(mac: str):
        """Add plugwise sensors for device."""
        entities: list[USBSensor] = []
        entities.extend(
            [
                USBSensor(api_stick.devices[mac], description)
                for description in PW_SENSOR_TYPES
                if description.plugwise_api == STICK
                and description.key in api_stick.devices[mac].features
            ]
        )
        if entities:
            async_add_entities(entities)

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.SENSOR]:
        hass.async_create_task(async_add_sensors(mac))

    def discoved_device(mac: str):
        """Add sensors for newly discovered device."""
        hass.async_create_task(async_add_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


async def async_setup_entry_gateway(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[PlugwiseSensorEntity] = []
    for device_id, device in coordinator.data.devices.items():
        await migrate_sensor_entity(hass, coordinator, device_id, device)
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
    
async def migrate_sensor_entity(
    hass: HomeAssistant,
    coordinator: PlugwiseDataUpdateCoordinator,
    device_id: str,
    device: str,
) -> None:
    """Migrate Sensors if needed."""
    ent_reg = entity_registry.async_get(hass)

    # Migrating opentherm_outdoor_temperature to opentherm_outdoor_air_temperature sensor
    if device["class"] == "heater_central":
        old_unique_id = f"{device_id}-outdoor_temperature"
        if entity_id := ent_reg.async_get_entity_id(
            Platform.SENSOR, DOMAIN, old_unique_id
        ):
            new_unique_id = f"{device_id}-outdoor_air_temperature"
            LOGGER.debug(
                "Migrating entity %s from old unique ID '%s' to new unique ID '%s'",
                entity_id,
                old_unique_id,
                new_unique_id,
            )
            ent_reg.async_update_entity(entity_id, new_unique_id=new_unique_id)


class PlugwiseSensorEntity(PlugwiseEntity, SensorEntity):
    """Represent Plugwise Sensors."""

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
        self._attr_name = (f"{self.device.get('name', '')} {description.name}").lstrip()

    @property
    def native_value(self) -> int | float | None:
        """Return the value reported by the sensor."""
        return self.device["sensors"].get(self.entity_description.key)


class USBSensor(PlugwiseUSBEntity, SensorEntity):
    """Representation of a Plugwise USB sensor."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseSensorEntityDescription
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(node, description)

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        state_value = getattr(self._node, self.entity_description.state_request_method)
        if state_value is not None:
            return float(round(state_value, 3))
        return None
