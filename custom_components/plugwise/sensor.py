"""Plugwise Sensor component for Home Assistant."""

import logging

from plugwise.smileclasses import AuxDevice, Gateway, Plug, Thermostat

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_STATE,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN

from .gateway import SmileGateway
from .usb import NodeEntity
from .const import (
    API,
    ATTR_ENABLED_DEFAULT,
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_CLASS,
    PW_MODEL,
    PW_TYPE,
    PW_TYPES,
    SMILE,
    STICK,
    STICK_API,
    SWITCH_CLASSES,
    DEVICE_THERMOSTAT_CLASSES,
    USB,
    USB_AVAILABLE_ID,
    USB_MOTION_ID,
    USB_RELAY_ID,
    VENDOR,
)

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
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    smile = hass.data[DOMAIN][config_entry.entry_id][SMILE]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    _LOGGER.debug("Plugwise sensor type %s", smile.s_type)

    entities = []

    for dev_id in smile.devices:
        for key, value in smile.devices[dev_id].items():
            if key != "sensors":
                continue

            for key, value in smile.devices[dev_id]["sensors"].items():
                entities.append(
                    GwSensor(
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


class GwSensor(SmileGateway, Entity):
    """Representation of a Smile Gateway sensor."""

    def __init__(
        self,
        api,
        coordinator,
        smile,
        name,
        dev_id,
        sensor,
        sr_data,
    ):
        """Initialise the switch."""
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
        self._plug = Plug(api, dev_id)
        self._thermostat = Thermostat(api, dev_id)

        self._api = api
        self._device_class = sr_data[ATTR_DEVICE_CLASS]
        self._device_name = name
        self._enabled_default = sr_data[ATTR_ENABLED_DEFAULT]
        self._icon = None
        self._name = f"{name} {sr_data[ATTR_NAME]}"
        self._sensor = sensor
        self._sr_data = sr_data
        self._state = None
        self._unit_of_measurement = None

        self._unique_id = f"{dev_id}-{sensor}"

    @property
    def device_class(self):
        """Return the device class of this entity, if any."""
        return self._device_class

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
        # _LOGGER.debug("Update sensor called")
        if self._smile.devices[self._dev_id][PW_CLASS] == "gateway":
            self._gateway.update_data()
        if any(dummy in self._smile.devices[self._dev_id][PW_TYPES] for dummy in SWITCH_CLASSES):
            self._plug.update_data()
        if self._smile.devices[self._dev_id][PW_CLASS] in DEVICE_THERMOSTAT_CLASSES:
            self._thermostat.update_data()
        if self._smile.devices[self._dev_id][PW_CLASS] == "heater_central":
            self._auxdev.update_data()

        self._state = self._sr_data[ATTR_STATE]
        self._icon = self._sr_data[ATTR_ICON]
        self.async_write_ha_state()


class USBSensor(NodeEntity):
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
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return STICK_API[self.sensor_id][ATTR_UNIT_OF_MEASUREMENT]
