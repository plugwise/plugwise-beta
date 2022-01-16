"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_NAME, Platform

from plugwise.nodes import PlugwiseNode

from .const import (
    CB_NEW_NODE,
    COORDINATOR,
    DOMAIN,
    FW,
    PW_MODEL,
    PW_TYPE,
    SMILE,
    STICK,
    USB,
    VENDOR,
)
from .gateway import SmileGateway
from .models import PW_SENSOR_TYPES, PlugwiseSensorEntityDescription
from .smile_helpers import icon_selector
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

    async def async_add_sensors(mac: str):
        """Add plugwise sensors for device."""
        entities = []
        entities.extend(
            [
                USBSensor(api_stick.devices[mac], description)
                for description in PW_SENSOR_TYPES
                if description.plugwise_api == STICK
                and description.key in api_stick.devices[mac].features
            ]
        )
        if entities:
            async_add_entities(entities)

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.SENSOR]:
        hass.async_create_task(async_add_sensors(mac))

    def discoved_device(mac: str):
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
        if "sensors" in coordinator.data[1][dev_id]:
            for sensor in coordinator.data[1][dev_id]["sensors"]:
                for description in PW_SENSOR_TYPES:
                    if description.plugwise_api == SMILE and description.key == sensor:
                        entities.extend(
                            [
                                GwSensor(
                                    coordinator,
                                    description,
                                    dev_id,
                                    sensor,
                                )
                            ]
                        )
                        _LOGGER.debug("Add %s sensor", description.key)

    if entities:
        async_add_entities(entities, True)


class GwSensor(SmileGateway, SensorEntity):
    """Representation of a Smile Gateway sensor."""

    def __init__(
        self,
        coordinator,
        description: PlugwiseSensorEntityDescription,
        dev_id,
        sensor,
    ):
        """Initialise the sensor."""
        super().__init__(
            coordinator,
            description,
            dev_id,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(ATTR_NAME),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
        )

        self._attr_name = f"{coordinator.data[1][dev_id].get(ATTR_NAME)} {description.name}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_should_poll = description.should_poll
        self._attr_unique_id = f"{dev_id}-{description.key}"
        self._attr_state_class = description.state_class

        self._dev_id = dev_id
        self._sensor = sensor

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data[1][self._dev_id]["sensors"][self._sensor]

    @property
    def icon(self):
        """Return an icon, when needed."""
        if self._sensor == "device_state":
            return icon_selector(self.native_value, None)


class USBSensor(PlugwiseUSBEntity, SensorEntity):
    """Representation of a Plugwise USB sensor."""

    def __init__(
        self, node: PlugwiseNode, description: PlugwiseSensorEntityDescription
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(node, description)

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        state_value = getattr(self._node, self.entity_description.state_request_method)
        if state_value is not None:
            return float(round(state_value, 3))
        return None
