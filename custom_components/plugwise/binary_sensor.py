"""Plugwise Binary Sensor component for Home Assistant."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise.nodes import PlugwiseNode  # pw-beta usb

from .const import ATTR_SCAN_DAYLIGHT_MODE  # pw-beta usb
from .const import ATTR_SCAN_RESET_TIMER  # pw-beta usb
from .const import ATTR_SCAN_SENSITIVITY_MODE  # pw-beta usb
from .const import ATTR_SED_CLOCK_INTERVAL  # pw-beta usb
from .const import ATTR_SED_CLOCK_SYNC  # pw-beta usb
from .const import ATTR_SED_MAINTENANCE_INTERVAL  # pw-beta usb
from .const import ATTR_SED_SLEEP_FOR  # pw-beta usb
from .const import ATTR_SED_STAY_ACTIVE  # pw-beta usb
from .const import CB_NEW_NODE  # pw-beta usb
from .const import COORDINATOR, DOMAIN, LOGGER, SEVERITIES, STICK
from .const import PW_TYPE  # pw-beta
from .const import SERVICE_USB_SCAN_CONFIG  # pw-beta usb
from .const import SERVICE_USB_SCAN_CONFIG_SCHEMA  # pw-beta usb
from .const import SERVICE_USB_SED_BATTERY_CONFIG  # pw-beta usb
from .const import SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA  # pw-beta usb
from .const import USB  # pw-beta usb
from .const import USB_MOTION_ID  # pw-beta usb
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .models import PW_BINARY_SENSOR_TYPES, PlugwiseBinarySensorEntityDescription
from .usb import PlugwiseUSBEntity  # pw-beta

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


async def async_setup_entry_usb(hass, config_entry, async_add_entities):  # pw-beta
    """Set up Plugwise binary sensor based on config_entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]
    platform = entity_platform.current_platform.get()

    async def async_add_binary_sensors(mac: str):
        """Add plugwise binary sensors for device."""
        entities: list[USBBinarySensor] = []
        entities.extend(
            [
                USBBinarySensor(api_stick.devices[mac], description)
                for description in PW_BINARY_SENSOR_TYPES
                if description.plugwise_api == STICK
                and description.key in api_stick.devices[mac].features
            ]
        )
        if entities:
            async_add_entities(entities)

        if USB_MOTION_ID in api_stick.devices[mac].features:
            LOGGER.debug("Add binary_sensors for %s", mac)

            # Register services
            platform.async_register_entity_service(
                SERVICE_USB_SCAN_CONFIG,
                SERVICE_USB_SCAN_CONFIG_SCHEMA,
                "_service_scan_config",
            )
            platform.async_register_entity_service(
                SERVICE_USB_SED_BATTERY_CONFIG,
                SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA,
                "_service_sed_battery_config",
            )

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.BINARY_SENSOR]:
        hass.async_create_task(async_add_binary_sensors(mac))

    def discoved_device(mac: str):
        """Add binary sensors for newly discovered device."""
        hass.async_create_task(async_add_binary_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


async def async_setup_entry_gateway(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile binary_sensors from a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR]

    entities: list[PlugwiseBinarySensorEntity] = []
    for device_id, device in coordinator.data.devices.items():
        for description in PW_BINARY_SENSOR_TYPES:
            if (
                "binary_sensors" not in device
                or description.key not in device["binary_sensors"]
            ):
                continue

            entities.append(
                PlugwiseBinarySensorEntity(
                    coordinator,
                    device_id,
                    description,
                )
            )
            LOGGER.debug("Add %s binary sensor", description.key)
    async_add_entities(entities)


class PlugwiseBinarySensorEntity(PlugwiseEntity, BinarySensorEntity):
    """Represent Smile Binary Sensors."""

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
        if (
            self._notification
        ):  # pw-beta: show Plugwise notifications as HA persistent notifications
            for notify_id, message in self._notification.items():
                self.hass.components.persistent_notification.async_create(
                    message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        return self.device["binary_sensors"].get(self.entity_description.key)

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


# pw-beta
# Github issue #265
class USBBinarySensor(PlugwiseUSBEntity, BinarySensorEntity):  # type: ignore[misc]
    """Representation of a Plugwise USB Binary Sensor."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseBinarySensorEntityDescription
    ) -> None:
        """Initialize a binary sensor entity."""
        super().__init__(node, description)

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        # Github issue #265
        return getattr(self._node, self.entity_description.state_request_method)  # type: ignore[attr-defined]

    def _service_scan_config(self, **kwargs):
        """Service call to configure motion sensor of Scan device."""
        sensitivity_mode = kwargs.get(ATTR_SCAN_SENSITIVITY_MODE)
        reset_timer = kwargs.get(ATTR_SCAN_RESET_TIMER)
        daylight_mode = kwargs.get(ATTR_SCAN_DAYLIGHT_MODE)
        LOGGER.debug(
            "Configure Scan device '%s': sensitivity='%s', reset timer='%s', daylight mode='%s'",
            self.name,
            sensitivity_mode,
            str(reset_timer),
            str(daylight_mode),
        )
        self._node.Configure_scan(reset_timer, sensitivity_mode, daylight_mode)

    def _service_sed_battery_config(self, **kwargs):
        """Configure battery powered (sed) device service call."""
        stay_active = kwargs.get(ATTR_SED_STAY_ACTIVE)
        sleep_for = kwargs.get(ATTR_SED_SLEEP_FOR)
        maintenance_interval = kwargs.get(ATTR_SED_MAINTENANCE_INTERVAL)
        clock_sync = kwargs.get(ATTR_SED_CLOCK_SYNC)
        clock_interval = kwargs.get(ATTR_SED_CLOCK_INTERVAL)
        LOGGER.debug(
            "Configure SED device '%s': stay active='%s', sleep for='%s', maintenance interval='%s', clock sync='%s', clock interval='%s'",
            self.name,
            str(stay_active),
            str(sleep_for),
            str(maintenance_interval),
            str(clock_sync),
            str(clock_interval),
        )
        self._node.Configure_SED(
            stay_active,
            maintenance_interval,
            sleep_for,
            clock_sync,
            clock_interval,
        )
