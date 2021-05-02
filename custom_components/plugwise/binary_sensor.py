"""Plugwise Binary Sensor component for Home Assistant."""

import logging
import voluptuous as vol

from plugwise.smileclasses import Gateway, AuxDevice

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_STATE,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import (
    API,
    ATTR_ENABLED_DEFAULT,
    ATTR_SCAN_DAYLIGHT_MODE,
    ATTR_SCAN_SENSITIVITY_MODE,
    ATTR_SCAN_RESET_TIMER,
    ATTR_SED_STAY_ACTIVE,
    ATTR_SED_SLEEP_FOR,
    ATTR_SED_MAINTENANCE_INTERVAL,
    ATTR_SED_CLOCK_SYNC,
    ATTR_SED_CLOCK_INTERVAL,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
    PW_CLASS,
    PW_MODEL,
    PW_TYPE,
    SCAN_SENSITIVITY_MODES,
    SERVICE_CONFIGURE_BATTERY,
    SERVICE_CONFIGURE_SCAN,
    SEVERITIES,
    SMILE,
    STICK,
    STICK_API,
    USB,
    USB_AVAILABLE_ID,
    USB_MOTION_ID,
    VENDOR,
)

from .gateway import SmileGateway
from .usb import NodeEntity

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

    async def async_add_binary_sensor(mac):
        """Add plugwise binary sensor."""
        if USB_MOTION_ID in api_stick.devices[mac].features:
            _LOGGER.debug("Add binary_sensors for %s", mac)
            async_add_entities([USBBinarySensor(api_stick.devices[mac])])

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
        hass.async_create_task(async_add_binary_sensor(mac))

    def discoved_binary_sensor(mac):
        """Add newly discovered binary sensor."""
        hass.async_create_task(async_add_binary_sensor(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_binary_sensor, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    smile = hass.data[DOMAIN][config_entry.entry_id][SMILE]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in smile.devices:
        for key, value in smile.devices[dev_id].items():
            if key != "binary_sensors":
                continue

            for key, value in smile.devices[dev_id]["binary_sensors"].items():
                entities.append(
                    GwBinarySensor(
                        api,
                        coordinator,
                        smile,
                        smile.devices[dev_id][ATTR_NAME],
                        dev_id,
                        key,
                        value,
                    )
                )

    async_add_entities(entities, True)


class GwBinarySensor(SmileGateway, BinarySensorEntity):
    """Representation of a Gateway binary_sensor."""

    def __init__(
        self,
        api,
        coordinator,
        smile,
        name,
        dev_id,
        binary_sensor,
        bs_data,
    ):
        """Initialise the binary_sensor."""
        super().__init__(
            coordinator,
            dev_id,
            smile,
            name,
            smile.devices[dev_id][PW_MODEL],
            smile.devices[dev_id][VENDOR],
            smile.devices[dev_id][FW],
        )

        self._auxdev = AuxDevice(api, dev_id)
        self._gateway = Gateway(api, dev_id)

        self._api = api
        self._smile = smile

        self._attributes = {}
        self._binary_sensor = binary_sensor
        self._bs_data = bs_data
        self._dev_id = dev_id
        self._device_class = self._bs_data[ATTR_DEVICE_CLASS]
        self._device_name = name
        if self._smile.devices[self._dev_id][PW_CLASS] == "gateway":
            self._device_name = f"Smile {name}"
        self._enabled_default = self._bs_data[ATTR_ENABLED_DEFAULT]
        self._icon = None
        self._is_on = False
        self._name = f"{name} {self._bs_data[ATTR_NAME]}"
        _LOGGER.debug(f"B_Sensor {self._name} is enabled: {self._enabled_default}")

        self._unique_id = f"{dev_id}-{binary_sensor}"

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

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
        # _LOGGER.debug("Update binary_sensor called")
        if self._smile.devices[self._dev_id][PW_CLASS] == "gateway":
            self._gateway.update_data()
            self._is_on = self._bs_data[ATTR_STATE]
            self._icon = NOTIFICATION_ICON if self._is_on else NO_NOTIFICATION_ICON

            notify = self._api.notifications
            for severity in SEVERITIES:
                self._attributes[f"{severity.upper()}_msg"] = []
            if notify != {}:
                for notify_id, details in notify.items():
                    for msg_type, msg in details.items():
                        if msg_type not in SEVERITIES:
                            msg_type = "other"

                        self._attributes[f"{msg_type.upper()}_msg"].append(msg)
                        self.hass.components.persistent_notification.async_create(
                            f"{msg_type.title()}: {msg}",
                            "Plugwise Notification:",
                            f"{DOMAIN}.{notify_id}",
                        )

        if self._smile.devices[self._dev_id][PW_CLASS] == "heater_central":
            self._auxdev.update_data()
            self._is_on = self._bs_data[ATTR_STATE]
            self._icon = self._bs_data[ATTR_ICON]

        self.async_write_ha_state()


class USBBinarySensor(NodeEntity, BinarySensorEntity):
    """Representation of a Stick Node Binary Sensor."""

    def __init__(self, node):
        """Initialize a Node entity."""
        super().__init__(node, USB_MOTION_ID)
        self.node_callbacks = (USB_AVAILABLE_ID, USB_MOTION_ID)

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return getattr(self._node, STICK_API[USB_MOTION_ID][ATTR_STATE])

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._node.mac}-{USB_MOTION_ID}"

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
            stay_active, maintenance_interval, sleep_for, clock_sync, clock_interval,
        )
