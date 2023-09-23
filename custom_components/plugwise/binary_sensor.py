"""Plugwise Binary Sensor component for Home Assistant."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from plugwise.constants import BinarySensorType

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COORDINATOR,  # pw-beta
    DOMAIN,
    LOGGER,
    SEVERITIES,
    UNIQUE_IDS,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


@dataclass
class PlugwiseBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Plugwise binary sensor entity."""

    key: BinarySensorType
    icon_off: str | None = None


BINARY_SENSORS: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key="compressor_state",
        translation_key="compressor_state",
        icon="mdi:hvac",
        icon_off="mdi:hvac-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="cooling_enabled",
        translation_key="cooling_enabled",
        icon="mdi:snowflake-thermometer",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="dhw_state",
        translation_key="dhw_state",
        icon="mdi:water-pump",
        icon_off="mdi:water-pump-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="flame_state",
        translation_key="flame_state",
        icon="mdi:fire",
        icon_off="mdi:fire-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="heating_state",
        translation_key="heating_state",
        icon="mdi:radiator",
        icon_off="mdi:radiator-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="cooling_state",
        translation_key="cooling_state",
        icon="mdi:snowflake",
        icon_off="mdi:snowflake-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="slave_boiler_state",
        translation_key="slave_boiler_state",
        icon="mdi:fire",
        icon_off="mdi:circle-off-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="plugwise_notification",
        translation_key="plugwise_notification",
        icon="mdi:mailbox-up-outline",
        icon_off="mdi:mailbox-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Plugwise binary sensor based on config_entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]
    current_unique_ids: set[tuple[str, str]] = hass.data[DOMAIN][config_entry.entry_id][
        UNIQUE_IDS
    ]

    entities: list[PlugwiseBinarySensorEntity] = []
    for device_id, device in coordinator.data.devices.items():
        if not (binary_sensors := device.get("binary_sensors")):
            continue
        for description in BINARY_SENSORS:
            if description.key not in binary_sensors:
                continue
            entities.append(
                PlugwiseBinarySensorEntity(
                    coordinator,
                    current_unique_ids,
                    device_id,
                    description,
                )
            )
            LOGGER.debug(
                "Add %s %s binary sensor", device["name"], description.translation_key
            )

    async_add_entities(entities)


class PlugwiseBinarySensorEntity(PlugwiseEntity, BinarySensorEntity):
    """Represent Smile Binary Sensors."""

    entity_description: PlugwiseBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        current_unique_ids: set[tuple[str, str]],
        device_id: str,
        description: PlugwiseBinarySensorEntityDescription,
    ) -> None:
        """Initialise the binary_sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        current_unique_ids.add(("binary_sensor", self._attr_unique_id))
        self._notification: dict[str, str] = {}  # pw-beta

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        # pw-beta: show Plugwise notifications as HA persistent notifications
        if self._notification:
            for notify_id, message in self._notification.items():
                self.hass.components.persistent_notification.async_create(
                    message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        # return self.device["binary_sensors"][self.entity_description.key]  # type: ignore [literal-required]
        return self.device["binary_sensors"][self.entity_description.key]

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if (icon_off := self.entity_description.icon_off) and self.is_on is False:
            return icon_off
        return self.entity_description.icon

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        if self.entity_description.key != "plugwise_notification":
            return None

        # pw-beta adjustment with attrs is to only represent severities *with* content
        # not all severities including those without content as empty lists
        attrs: dict[str, list[str]] = {}  # pw-beta Re-evaluate against Core
        self._notification = {}  # pw-beta
        if notify := self.coordinator.data.gateway["notifications"]:
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
