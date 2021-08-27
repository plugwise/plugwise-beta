"""Plugwise Sensor component for Home Assistant."""

import logging

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_ID,
    ATTR_NAME,
    ATTR_STATE,
    ATTR_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import callback

from .const import (
    ATTR_ENABLED_DEFAULT,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_MODEL,
    PW_TYPE,
    STICK,
    STICK_API,
    USB,
    USB_AVAILABLE_ID,
    USB_ENERGY_CONSUMPTION_TODAY_ID,
    USB_MOTION_ID,
    USB_RELAY_ID,
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
    """Set up Plugwise sensor based on config_entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_sensor(mac):
        """Add plugwise sensor."""
        for feature in api_stick.devices[mac].features:
            if feature not in (USB_MOTION_ID, USB_RELAY_ID):
                async_add_entities([USBSensor(api_stick.devices[mac], feature)])

    for mac in hass.data[DOMAIN][config_entry.entry_id][SENSOR_DOMAIN]:
        hass.async_create_task(async_add_sensor(mac))

    def discoved_sensor(mac):
        """Add newly discovered sensor."""
        hass.async_create_task(async_add_sensor(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_sensor, CB_NEW_NODE)


async def async_setup_entry_gateway(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug("Plugwise hass data %s", hass.data[DOMAIN])
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in coordinator.data[1]:
        for key in coordinator.data[1][dev_id]:
            if key != "sensors":
                continue

            for data in coordinator.data[1][dev_id]["sensors"]:
                entities.append(
                    GwSensor(
                        api,
                        coordinator,
                        dev_id,
                        coordinator.data[1][dev_id].get(ATTR_NAME),
                        data,
                    )
                )

    async_add_entities(entities, True)


class GwSensor(SmileGateway, SensorEntity):
    """Representation of a Smile Gateway sensor."""

    def __init__(
        self,
        coordinator,
        dev_id,
        name,
        sr_data,
    ):
        """Initialise the sensor."""
        super().__init__(
            coordinator,
            dev_id,
            name,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
        )

        self._attr_state_class = sr_data.get("state_class")
        self._attr_last_reset = sr_data.get("last_reset")
        self._device_class = sr_data.get(ATTR_DEVICE_CLASS)
        self._device_name = name
        self._enabled_default = sr_data.get(ATTR_ENABLED_DEFAULT)
        self._icon = None
        self._name = f"{name} {sr_data.get(ATTR_NAME)}"
        self._sensor = sr_data.get(ATTR_ID)
        self._sr_data = sr_data
        self._state = None
        self._unit_of_measurement = self._sr_data.get(ATTR_UNIT_OF_MEASUREMENT)

        self._unique_id = f"{dev_id}-{self._sensor}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._enabled_default

    @property
    def icon(self):
        """Return the icon of this entity."""
        return self._icon

    @property
    def state(self):
        """Return the state of this entity."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._icon = self._sr_data.get(ATTR_ICON)
        self._state = self._sr_data.get(ATTR_STATE)

        self.async_write_ha_state()


class USBSensor(NodeEntity, SensorEntity):
    """Representation of a Stick Node sensor."""

    def __init__(self, node, sensor_id):
        """Initialize a Node entity."""
        super().__init__(node, sensor_id)
        self.sensor_id = sensor_id
        self.node_callbacks = (USB_AVAILABLE_ID, sensor_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        state_value = getattr(self._node, STICK_API[self.sensor_id][ATTR_STATE])
        if state_value is not None:
            return float(round(state_value, 3))
        return None

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._node.mac}-{self.sensor_id}"

    @property
    def last_reset(self):
        """Last reset timestamp of measurement state class."""
        if self.sensor_id == USB_ENERGY_CONSUMPTION_TODAY_ID:
            return self._node.energy_consumption_today_last_reset
        return None

    @property
    def state_class(self):
        """Return the state class."""
        if self.sensor_id == USB_ENERGY_CONSUMPTION_TODAY_ID:
            return "measurement"
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return STICK_API[self.sensor_id][ATTR_UNIT_OF_MEASUREMENT]
