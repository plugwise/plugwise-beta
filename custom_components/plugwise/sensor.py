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

from plugwise.nodes import PlugwiseNode

from .const import (
    ATTR_ENABLED_DEFAULT,
    CB_NEW_NODE,
    COOLING_ICON,
    COORDINATOR,
    DOMAIN,
    FLAME_ICON,
    FW,
    HEATING_ICON,
    IDLE_ICON,
    PW_MODEL,
    PW_TYPE,
    SMILE,
    STICK,
    USB,
    VENDOR,
)
from .gateway import SmileGateway
from .models import PW_SENSOR_TYPES, PlugwiseSensorEntityDescription
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

    for mac in hass.data[DOMAIN][config_entry.entry_id][SENSOR_DOMAIN]:
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
        for key in coordinator.data[1][dev_id]:
            if key != "sensors":
                continue

            for data in coordinator.data[1][dev_id]["sensors"]:
                for description in PW_SENSOR_TYPES:
                    if (
                        description.plugwise_api == SMILE
                        and description.key == data.get(ATTR_ID)
                    ):
                        entities.extend(
                            [
                                GwSensor(
                                    coordinator,
                                    dev_id,
                                    coordinator.data[1][dev_id].get(ATTR_NAME),
                                    data,
                                    description,
                                )
                            ]
                        )

    if entities:
        async_add_entities(entities, True)


class GwSensor(SmileGateway, SensorEntity):
    """Representation of a Smile Gateway sensor."""

    def __init__(
        self,
        coordinator,
        dev_id,
        name,
        sr_data,
        description: PlugwiseSensorEntityDescription,
    ):
        """Initialise the sensor."""
        super().__init__(
            coordinator,
            dev_id,
            name,
            coordinator.data[1][dev_id].get(PW_MODEL),
            coordinator.data[1][dev_id].get(VENDOR),
            coordinator.data[1][dev_id].get(FW),
            description,
        )

        self._attr_device_class = description.device_class
        self._attr_entity_registry_enabled_default = (
            description.entity_registry_enabled_default
        )
        self._attr_icon = description.icon
        self._attr_name = f"{name} {description.name}"
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_should_poll = self.entity_description.should_poll
        self._attr_state_class = description.state_class
        self._attr_unique_id = f"{dev_id}-{description.key}"
        self._sr_data = sr_data

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._attr_native_value = self._sr_data.get(ATTR_STATE)

        if self._sr_data.get(ATTR_ID) == "device_state":
            self._attr_icon = IDLE_ICON
            if self._attr_native_value == "dhw-heating":
                self._attr_icon = FLAME_ICON
            if self._attr_native_value == "heating":
                self._attr_icon = HEATING_ICON
            if self._attr_native_value == "dhw and heating":
                self._attr_icon = HEATING_ICON
            if self._attr_native_value == "cooling":
                self._attr_icon = COOLING_ICON
            if self._attr_native_value == "dhw and cooling":
                self._attr_icon = COOLING_ICON

        self.async_write_ha_state()


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
