"""Plugwise Binary Sensor component for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from plugwise.nodes import PlugwiseNode

from .const import (
    ATTR_SCAN_DAYLIGHT_MODE,
    ATTR_SCAN_RESET_TIMER,
    ATTR_SCAN_SENSITIVITY_MODE,
    ATTR_SED_CLOCK_INTERVAL,
    ATTR_SED_CLOCK_SYNC,
    ATTR_SED_MAINTENANCE_INTERVAL,
    ATTR_SED_SLEEP_FOR,
    ATTR_SED_STAY_ACTIVE,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_MODEL,
    PW_TYPE,
    SERVICE_USB_SCAN_CONFIG,
    SERVICE_USB_SCAN_CONFIG_SCHEMA,
    SERVICE_USB_SED_BATTERY_CONFIG,
    SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA,
    STICK,
    USB,
    USB_MOTION_ID,
    VENDOR,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseGatewayEntity
from .models import PW_BINARY_SENSOR_TYPES, PlugwiseBinarySensorEntityDescription
from .smile_helpers import GWBinarySensor, icon_selector
from .usb import PlugwiseUSBEntity

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)


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
            _LOGGER.debug("Add binary_sensors for %s", mac)

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


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[GwBinarySensor] = []
    for device_id, device_properties in coordinator.data.devices.items():
        for description in PW_BINARY_SENSOR_TYPES:
            if (
                "binary_sensors" not in device_properties
                or description.key not in device_properties["binary_sensors"]
            ):
                continue

            entities.append(
                GatewayBinarySensorEntity(
                    coordinator,
                    description,
                    device_id,
                )
            )
            _LOGGER.debug("Add %s binary sensor", description.key)

    if entities:
        async_add_entities(entities, True)


class GatewayBinarySensorEntity(PlugwiseGatewayEntity, BinarySensorEntity):
    """Represent Smile Binary Sensors."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        description: PlugwiseBinarySensorEntityDescription,
        device_id: str,
    ) -> None:
        """Initialise the binary_sensor."""
        super().__init__(
            coordinator,
            description,
            device_id,
            coordinator.data.devices[device_id].get(PW_MODEL),
            coordinator.data.devices[device_id].get(ATTR_NAME),
            coordinator.data.devices[device_id].get(VENDOR),
            coordinator.data.devices[device_id].get(FW),
        )

        self.gw_b_sensor = GWBinarySensor(coordinator.data)

        self._attr_entity_registry_enabled_default = (
            description.entity_registry_enabled_default
        )
        self._attr_extra_state_attributes = None
        self._attr_icon = None
        self._attr_is_on = False
        self._attr_name = (
            f"{coordinator.data.devices[device_id].get(ATTR_NAME)} {description.name}"
        )
        self._attr_should_poll = self.entity_description.should_poll
        self._attr_unique_id = f"{device_id}-{description.key}"
        self.binary_sensor = description.key
        self.device_id = device_id

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        return self.gw_b_sensor.extra_state_attributes

    @property
    def is_on(self) -> bool:
        """Update the state of the Binary Sensor."""
        if self.gw_b_sensor.notification:
            for notify_id, message in self.gw_b_sensor.notification.items():
                self.hass.components.persistent_notification.async_create(
                    message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        return self.coordinator.data.devices[self.device_id]["binary_sensors"][
            self.binary_sensor
        ]

    @property
    def icon(self):
        """Gateway binary_sensor icon."""
        return icon_selector(self.binary_sensor, self.is_on)


class USBBinarySensor(PlugwiseUSBEntity, BinarySensorEntity):
    """Representation of a Plugwise USB Binary Sensor."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseBinarySensorEntityDescription
    ) -> None:
        """Initialize a binary sensor entity."""
        super().__init__(node, description)

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return getattr(self._node, self.entity_description.state_request_method)

    def _service_scan_config(self, **kwargs):
        """Service call to configure motion sensor of Scan device."""
        sensitivity_mode = kwargs.get(ATTR_SCAN_SENSITIVITY_MODE)
        reset_timer = kwargs.get(ATTR_SCAN_RESET_TIMER)
        daylight_mode = kwargs.get(ATTR_SCAN_DAYLIGHT_MODE)
        _LOGGER.debug(
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
        _LOGGER.debug(
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
