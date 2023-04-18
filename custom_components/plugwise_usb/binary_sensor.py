"""Plugwise USB Binary Sensor component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from plugwise_usb.nodes import PlugwiseNode  # pw-beta usb

from . import PlugwiseUSBEntity  # pw-beta
from .const import (  # pw-beta usb
    ATTR_SCAN_DAYLIGHT_MODE,
    ATTR_SCAN_RESET_TIMER,
    ATTR_SCAN_SENSITIVITY_MODE,
    ATTR_SED_CLOCK_INTERVAL,
    ATTR_SED_CLOCK_SYNC,
    ATTR_SED_MAINTENANCE_INTERVAL,
    ATTR_SED_SLEEP_FOR,
    ATTR_SED_STAY_ACTIVE,
    CB_NEW_NODE,
    DOMAIN,
    LOGGER,
    SERVICE_USB_SCAN_CONFIG,
    SERVICE_USB_SCAN_CONFIG_SCHEMA,
    SERVICE_USB_SED_BATTERY_CONFIG,
    SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA,
    STICK,
    USB_MOTION_ID,
)
from .models import PW_BINARY_SENSOR_TYPES, PlugwiseBinarySensorEntityDescription

# mypy: disable-error-code="union-attr"


PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Plugwise USB binary sensor based on config_entry."""
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
            # mypy ignore because of error: Item "None" of "Optional[EntityPlatform]" has no attribute "async_register_entity_service" [union-attr]
            platform.async_register_entity_service(
                SERVICE_USB_SED_BATTERY_CONFIG,
                SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA,
                "_service_sed_battery_config",
            )
            # mypy ignore because of error: Item "None" of "Optional[EntityPlatform]" has no attribute "async_register_entity_service" [union-attr]

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.BINARY_SENSOR]:
        hass.async_create_task(async_add_binary_sensors(mac))

    def discoved_device(mac: str):
        """Add binary sensors for newly discovered device."""
        hass.async_create_task(async_add_binary_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


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
