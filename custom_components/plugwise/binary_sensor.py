"""Plugwise Binary Sensor component for Home Assistant."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_ID, ATTR_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform

from plugwise.entities import GWBinarySensor

from .const import (
    ATTR_ENABLED_DEFAULT,
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
    PW_CLASS,
    PW_MODEL,
    PW_TYPE,
    SCAN_SENSITIVITY_MODES,
    SERVICE_CONFIGURE_BATTERY,
    SERVICE_CONFIGURE_SCAN,
    STICK,
    USB,
    USB_BINARY_SENSOR_TYPES,
    USB_MOTION_ID,
    VENDOR,
)
from .gateway import SmileGateway
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

    async def async_add_binary_sensors(mac):
        """Add plugwise binary sensors for device."""
        entities = []
        entities.extend(
            [
                USBBinarySensor(api_stick.devices[mac], description)
                for description in USB_BINARY_SENSOR_TYPES
                if description.key in api_stick.devices[mac].features
            ]
        )
        async_add_entities(entities)

        if USB_MOTION_ID in api_stick.devices[mac].features:
            _LOGGER.debug("Add binary_sensors for %s", mac)

            # Register services
            platform.async_register_entity_service(
                SERVICE_CONFIGURE_SCAN,
                {
                    vol.Required(ATTR_SCAN_SENSITIVITY_MODE): vol.In(
                        SCAN_SENSITIVITY_MODES
                    ),
                    vol.Required(ATTR_SCAN_RESET_TIMER): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=240)
                    ),
                    vol.Required(ATTR_SCAN_DAYLIGHT_MODE): cv.boolean,
                },
                "_service_configure_scan",
            )
            platform.async_register_entity_service(
                SERVICE_CONFIGURE_BATTERY,
                {
                    vol.Required(ATTR_SED_STAY_ACTIVE): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=120)
                    ),
                    vol.Required(ATTR_SED_SLEEP_FOR): vol.All(
                        vol.Coerce(int), vol.Range(min=10, max=60)
                    ),
                    vol.Required(ATTR_SED_MAINTENANCE_INTERVAL): vol.All(
                        vol.Coerce(int), vol.Range(min=5, max=1440)
                    ),
                    vol.Required(ATTR_SED_CLOCK_SYNC): cv.boolean,
                    vol.Required(ATTR_SED_CLOCK_INTERVAL): vol.All(
                        vol.Coerce(int), vol.Range(min=60, max=10080)
                    ),
                },
                "_service_configure_battery_savings",
            )

    for mac in hass.data[DOMAIN][config_entry.entry_id][BINARY_SENSOR_DOMAIN]:
        hass.async_create_task(async_add_binary_sensors(mac))

    def discoved_device(mac):
        """Add binary sensors for newly discovered device."""
        hass.async_create_task(async_add_binary_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in coordinator.data[1]:
        for key in coordinator.data[1][dev_id]:
            if key != "binary_sensors":
                continue

            for data in coordinator.data[1][dev_id]["binary_sensors"]:
                entities.append(
                    GwBinarySensor(
                        coordinator,
                        dev_id,
                        coordinator.data[1][dev_id].get(ATTR_NAME),
                        data,
                    )
                )

    async_add_entities(entities, True)


class GwBinarySensor(SmileGateway, BinarySensorEntity):
    """Representation of a Gateway binary_sensor."""

    def __init__(
        self,
        coordinator,
        dev_id,
        name,
        bs_data,
    ):
        """Initialise the binary_sensor."""
        super().__init__(
            coordinator,
            dev_id,
            name,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
        )

        self._cdata = coordinator.data
        self._gw_b_sensor = GWBinarySensor(self._cdata, dev_id, bs_data[ATTR_ID])
        self._attributes = {}
        self._binary_sensor = bs_data.get(ATTR_ID)
        self._bs_data = bs_data
        self._dev_id = dev_id
        self._device_class = None
        self._device_name = name
        if self._cdata[1][self._dev_id][PW_CLASS] == "gateway":
            self._device_name = f"Smile {name}"
        self._enabled_default = self._bs_data.get(ATTR_ENABLED_DEFAULT)
        self._icon = None
        self._is_on = False
        self._name = f"{name} {self._bs_data.get(ATTR_NAME)}"
        self._unique_id = f"{dev_id}-{self._binary_sensor}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon of this entity."""
        return self._icon

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._gw_b_sensor.update_data()
        self._attributes = self._gw_b_sensor.extra_state_attributes
        self._is_on = self._gw_b_sensor.is_on
        self._icon = self._gw_b_sensor.icon

        if self._gw_b_sensor.notification:
            for notify_id, message in self._gw_b_sensor.notification.items():
                self.hass.components.persistent_notification.async_create(
                    message, "Plugwise Notification:", f"{DOMAIN}.{notify_id}"
                )

        self.async_write_ha_state()


class USBBinarySensor(PlugwiseUSBEntity, BinarySensorEntity):
    """Representation of a Plugwise USB Binary Sensor."""

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return getattr(self._node, self.entity_description.state_request_method)

    def _service_configure_scan(self, **kwargs):
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

    def _service_configure_battery_savings(self, **kwargs):
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
