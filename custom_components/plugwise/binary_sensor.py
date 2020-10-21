"""Plugwise Binary Sensor component for Home Assistant."""

import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_OFF, STATE_ON
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
    AVAILABLE_SENSOR_ID,
    BINARY_SENSORS,
    BINARY_SENSOR_MAP,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FLAME_ICON,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    IDLE_ICON,
    MOTION_SENSOR_ID,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
    PW_TYPE,
    SCAN_SENSITIVITY_MODES,
    SERVICE_CONFIGURE_BATTERY,
    SERVICE_CONFIGURE_SCAN,
    STICK,
    USB,
)

from .sensor import SmileSensor
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
    stick = hass.data[DOMAIN][config_entry.entry_id][STICK]
    platform = entity_platform.current_platform.get()

    async def async_add_sensor(mac):
        """Add plugwise sensor."""
        _LOGGER.debug("Add binary_sensors for %s", mac)

        node = stick.node(mac)
        for sensor_type in node.get_sensors():
            if sensor_type in BINARY_SENSORS:
                async_add_entities([USBBinarySensor(node, mac, sensor_type)])
                ## TODO: two strings in debug, wont work and doesnt display what you want
                _LOGGER.debug("Added %s as binary_sensors for %s", mac)

                if node.get_node_type() == "Scan" and sensor_type == MOTION_SENSOR_ID:
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

    for mac in hass.data[DOMAIN][config_entry.entry_id]["binary_sensor"]:
        hass.async_create_task(async_add_sensor(mac))

    def discoved_binary_sensor(mac):
        """Add newly discovered binary sensor."""
        hass.async_create_task(async_add_sensor(mac))

    # Listen for discovered nodes
    stick.subscribe_stick_callback(discoved_binary_sensor, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    is_thermostat = api.single_master_thermostat()

    all_devices = api.get_all_devices()
    for dev_id, device_properties in all_devices.items():
        if device_properties["class"] == "heater_central":
            _LOGGER.debug("Plugwise device_class %s found", device_properties["class"])
            data = api.get_device_data(dev_id)
            for binary_sensor, dummy in BINARY_SENSOR_MAP.items():
                _LOGGER.debug("Binary_sensor: %s", binary_sensor)
                if binary_sensor not in data:
                    continue

                _LOGGER.debug(
                    "Plugwise binary_sensor Dev %s", device_properties["name"]
                )
                entities.append(
                    GwBinarySensor(
                        api,
                        coordinator,
                        device_properties["name"],
                        dev_id,
                        binary_sensor,
                        device_properties["class"],
                    )
                )
                _LOGGER.info(
                    "Added binary_sensor.%s",
                    f"{device_properties['name']}_{binary_sensor}",
                )
        if device_properties["class"] == "gateway" and is_thermostat is not None:
            _LOGGER.debug("Plugwise device_class %s found", device_properties["class"])
            entities.append(
                GwNotifySensor(
                    hass,
                    api,
                    coordinator,
                    device_properties["name"],
                    dev_id,
                    True,
                    "plugwise_notification",
                    device_properties["class"],
                )
            )
            _LOGGER.info(
                "Added binary_sensor.%s",
                f"{device_properties['name']}_{'plugwise_notification'}",
            )

    async_add_entities(entities, True)


class GwBinarySensor(SmileSensor, BinarySensorEntity):
    """Representation of a Plugwise binary_sensor."""

    def __init__(
        self, api, coordinator, name, dev_id, enabled_default, binary_sensor, model
    ):
        """Set up the Plugwise API."""
        self._enabled_default = enabled_default, True

        super().__init__(
            api, coordinator, name, dev_id, self._enabled_default, binary_sensor
        )

        self._binary_sensor = binary_sensor

        self._is_on = False
        self._icon = None
        self._state = None

        self._unique_id = f"{dev_id}-{binary_sensor}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update binary_sensor called")
        data = self._api.get_device_data(self._dev_id)

        if self._binary_sensor not in data:
            self.async_write_ha_state()
            return

        self._is_on = data[self._binary_sensor]

        self._state = STATE_ON if self._is_on else STATE_OFF
        if self._binary_sensor == "dhw_state":
            self._icon = FLOW_ON_ICON if self._is_on else FLOW_OFF_ICON
        if self._binary_sensor == "slave_boiler_state":
            self._icon = FLAME_ICON if self._is_on else IDLE_ICON

        self.async_write_ha_state()


class GwNotifySensor(GwBinarySensor, BinarySensorEntity):
    """Representation of a Plugwise Notification binary_sensor."""

    def __init__(
        self,
        hass,
        api,
        coordinator,
        name,
        dev_id,
        enabled_default,
        binary_sensor,
        model,
    ):
        """Set up the Plugwise API."""
        self._enabled_default = enabled_default, True

        super().__init__(
            api, coordinator, name, dev_id, self._enabled_default, binary_sensor, model
        )

        self._binary_sensor = binary_sensor
        self._hass = hass

        self._is_on = False
        self._icon = None
        self._attributes = {}

        self._unique_id = f"{dev_id}-{binary_sensor}"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._attributes = {}

        notify = self._api.notifications

        self._is_on = False
        self._state = STATE_OFF
        self._icon = NO_NOTIFICATION_ICON

        if notify != {}:
            self._is_on = True
            self._state = STATE_ON
            self._icon = NOTIFICATION_ICON

            for notify_id, details in notify.items():
                for msg_type, msg in details.items():
                    self._attributes[msg_type.upper()] = msg
                    self._hass.components.persistent_notification.async_create(
                        f"{msg_type.upper()}: {msg}",
                        "Plugwise Notification:",
                        f"{DOMAIN}.{notify_id}",
                    )

        self.async_write_ha_state()


class USBBinarySensor(NodeEntity, BinarySensorEntity):
    """Representation of a Plugwise Binary Sensor."""

    def __init__(self, node, mac, sensor_id):
        """Initialize a Node entity."""
        super().__init__(node, mac)
        self.sensor_id = sensor_id
        self.sensor_type = BINARY_SENSORS[sensor_id]
        self.node_callbacks = (AVAILABLE_SENSOR_ID, sensor_id)

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self.sensor_type["class"]

    @property
    def entity_registry_enabled_default(self):
        """Return the sensor registration state."""
        return self.sensor_type[ATTR_ENABLED_DEFAULT]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.sensor_type["icon"]

    @property
    def name(self):
        """Return the display name of this sensor."""
        return f"{self.sensor_type['name']} ({self._mac[-5:]})"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return getattr(self._node, self.sensor_type["state"])()

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._mac}-{self.sensor_id}"

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
