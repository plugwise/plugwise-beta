"""Plugwise Binary Sensor component for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_NAME
from homeassistant.core import callback
from homeassistant.helpers import entity_platform

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
    SMILE,
    STICK,
    USB,
    USB_MOTION_ID,
    VENDOR,
)
from .gateway import SmileGateway
from .models import PW_BINARY_SENSOR_TYPES, PlugwiseBinarySensorEntityDescription
from .smile_helpers import GWBinarySensor
from .usb import PlugwiseUSBEntity

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
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
        entities = []
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

    for mac in hass.data[DOMAIN][config_entry.entry_id][BINARY_SENSOR_DOMAIN]:
        hass.async_create_task(async_add_binary_sensors(mac))

    def discoved_device(mac: str):
        """Add binary sensors for newly discovered device."""
        hass.async_create_task(async_add_binary_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in coordinator.data[1]:
        if "binary_sensors" in coordinator.data[1][dev_id]:
            for b_sensor in coordinator.data[1][dev_id]["binary_sensors"]:
                for description in PW_BINARY_SENSOR_TYPES:
                    if (
                        description.plugwise_api == SMILE
                        and description.key == b_sensor
                    ):
                        entities.extend(
                            [
                                GwBinarySensor(
                                    coordinator,
                                    description,
                                    dev_id,
                                    b_sensor,
                                )
                            ]
                        )

    if entities:
        async_add_entities(entities, True)


class GwBinarySensor(SmileGateway, BinarySensorEntity):
    """Representation of a Gateway binary_sensor."""

    def __init__(
        self,
        coordinator,
        description: PlugwiseBinarySensorEntityDescription,
        dev_id,
        b_sensor,
    ):
        """Initialise the binary_sensor."""
        _cdata = coordinator.data[1][dev_id]
        super().__init__(
            coordinator,
            description,
            dev_id,
            _cdata.get(PW_MODEL),
            _cdata.get(ATTR_NAME),
            _cdata.get(VENDOR),
            _cdata.get(FW),
        )

        self._gw_b_sensor = GWBinarySensor(coordinator.data, dev_id, b_sensor)

        self._attr_entity_registry_enabled_default = (
            description.entity_registry_enabled_default
        )
        self._attr_extra_state_attributes = None
        self._attr_icon = None
        self._attr_is_on = False
        self._attr_name = f"{_cdata.get(ATTR_NAME)} {description.name}"
        self._attr_should_poll = self.entity_description.should_poll
        self._attr_unique_id = f"{dev_id}-{description.key}"

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._gw_b_sensor.update_data()
        self._attr_extra_state_attributes = self._gw_b_sensor.extra_state_attributes
        self._attr_icon = self._gw_b_sensor.icon
        self._attr_is_on = self._gw_b_sensor.is_on

        if self._gw_b_sensor.notification:
            for notify_id, message in self._gw_b_sensor.notification.items():
                self.hass.components.persistent_notification.async_create(
                    message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        self.async_write_ha_state()


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
