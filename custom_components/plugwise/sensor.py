"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

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
    USB,
    USB_MOTION_ID,
    USB_RELAY_ID,
    USB_SENSOR_TYPES,
    VENDOR,
    PlugwiseUSBSensorEntityDescription,
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
    """Set up Plugwise sensor based on config_entry."""
    api_stick = hass.data[DOMAIN][config_entry.entry_id][STICK]

    async def async_add_sensors(mac):
        """Add plugwise sensors for device."""
        entities = []
        entities.extend(
            [
                USBSensor(api_stick.devices[mac], description)
                for description in USB_SENSOR_TYPES
                if description.key in api_stick.devices[mac].features
            ]
        )
        async_add_entities(entities)

    for mac in hass.data[DOMAIN][config_entry.entry_id][SENSOR_DOMAIN]:
        hass.async_create_task(async_add_sensors(mac))

    def discoved_device(mac):
        """Add sensors for newly discovered device."""
        hass.async_create_task(async_add_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


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


class USBSensor(PlugwiseUSBEntity, SensorEntity):
    """Representation of a Plugwise USB sensor."""

    def __init__(self, node, description: PlugwiseUSBSensorEntityDescription):
        """Initialize sensor entity."""
        super().__init__(node, description)

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        state_value = getattr(self._node, self.entity_description.state_request_method)
        if state_value is not None:
            return float(round(state_value, 3))
        return None
