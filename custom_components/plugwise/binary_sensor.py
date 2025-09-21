"""Plugwise Binary Sensor component for Home Assistant."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from plugwise.constants import BinarySensorType

from homeassistant.components import (
    persistent_notification,  # pw-beta Plugwise notifications
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    BATTERY_STATE,
    BINARY_SENSORS,
    COMPRESSOR_STATE,
    COOLING_ENABLED,
    COOLING_STATE,
    DHW_STATE,
    DOMAIN,
    FLAME_STATE,
    HEATING_STATE,
    LOGGER,  # pw-beta
    PLUGWISE_NOTIFICATION,
    SECONDARY_BOILER_STATE,
    SEVERITIES,
)

# Upstream
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class PlugwiseBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Plugwise binary sensor entity."""

    key: BinarySensorType


# Upstream PLUGWISE_BINARY_SENSORS
PLUGWISE_BINARY_SENSORS: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key=BATTERY_STATE,
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=COMPRESSOR_STATE,
        translation_key=COMPRESSOR_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=COOLING_ENABLED,
        translation_key=COOLING_ENABLED,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=DHW_STATE,
        translation_key=DHW_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=FLAME_STATE,
        translation_key=FLAME_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=HEATING_STATE,
        translation_key=HEATING_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=COOLING_STATE,
        translation_key=COOLING_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=SECONDARY_BOILER_STATE,
        translation_key=SECONDARY_BOILER_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=PLUGWISE_NOTIFICATION,
        translation_key=PLUGWISE_NOTIFICATION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Plugwise binary_sensors from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        # Upstream consts to HA
        # async_add_entities(
        #     PlugwiseBinarySensorEntity(coordinator, device_id, description)
        #     for device_id in coordinator.new_devices
        #     if (
        #         binary_sensors := coordinator.data.devices[device_id].get(
        #             BINARY_SENSORS
        #         )
        #     )
        #     for description in PLUGWISE_BINARY_SENSORS
        #     if description.key in binary_sensors
        # )

        # pw-beta alternative for debugging
        entities: list[PlugwiseBinarySensorEntity] = []
        for device_id in coordinator.new_devices:
            device = coordinator.data[device_id]
            if not (binary_sensors := device.get(BINARY_SENSORS)):
                continue
            for description in PLUGWISE_BINARY_SENSORS:
                if description.key not in binary_sensors:
                    continue
                entities.append(PlugwiseBinarySensorEntity(coordinator, device_id, description))
                LOGGER.debug(
                    "Add %s %s binary sensor", device["name"], description.translation_key
                )
        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseBinarySensorEntity(PlugwiseEntity, BinarySensorEntity):
    """Set up Plugwise binary_sensors from a config entry."""

    entity_description: PlugwiseBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseBinarySensorEntityDescription,
    ) -> None:
        """Initialise the binary_sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._notification: dict[str, str] = {}  # pw-beta

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        # pw-beta: show Plugwise notifications as HA persistent notifications
        if self._notification:
            for notify_id, message in self._notification.items():
                persistent_notification.async_create(
                    self.hass, message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        return self.device.get(BINARY_SENSORS, {}).get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        if self.entity_description.key != PLUGWISE_NOTIFICATION:  # Upstream const
            return None

        # pw-beta adjustment with attrs is to only represent severities *with* content
        # not all severities including those without content as empty lists
        attrs: dict[str, list[str]] = {}  # pw-beta Re-evaluate against Core
        self._notification = {}  # pw-beta
        gateway_id = self.coordinator.api.gateway_id
        if notify := self.coordinator.data[gateway_id]["notifications"]:
            for notify_id, details in notify.items():  # pw-beta uses notify_id
                for msg_type, msg in details.items():
                    msg_type = msg_type.lower()
                    if msg_type not in SEVERITIES:
                        msg_type = "other"  # pragma: no cover

                    if (
                        f"{msg_type}_msg" not in attrs
                    ):  # pw-beta Re-evaluate against Core
                        attrs[f"{msg_type}_msg"] = []
                    attrs[f"{msg_type}_msg"].append(msg)

                    self._notification[
                        notify_id
                    ] = f"{msg_type.title()}: {msg}"  # pw-beta

        return attrs
