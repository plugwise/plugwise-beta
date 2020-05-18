"""Plugwise Binary Sensor component for Home Assistant."""

import logging
from typing import Dict

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_OPENING,
    BinarySensorDevice,
)
from homeassistant.const import STATE_OFF, STATE_ON

from .const import (
    DOMAIN,
    FLAME_ICON,    
    VALVE_CLOSED_ICON,
    VALVE_OPEN_ICON,
    WATER_ICON,
)

from . import SmileGateway

BINARY_SENSOR_LIST = [
    "dhw_state",
    "slave_boiler_state",
    "valve_position",
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile binary_sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    devices = []
    binary_sensor_classes = [
        "heater_central",
        "thermo_sensor",
        "thermostatic_radiator_valve",
    ]
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():
        if device["class"] in binary_sensor_classes:
            _LOGGER.debug("Plugwise device_class %s found", device["class"])
            data = api.get_device_data(dev_id)
            for binary_sensor in BINARY_SENSOR_LIST:
                _LOGGER.debug("Binary_sensor: %s", binary_sensor)
                if binary_sensor in data:
                    _LOGGER.debug("Plugwise binary_sensor Dev %s", device["name"])
                    devices.append(
                        PwBinarySensor(
                            api,
                            coordinator,
                            device["name"],
                            binary_sensor,
                            dev_id,
                            device["class"],
                        )
                    )
                    _LOGGER.info("Added binary_sensor.%s", device["name"])

    async_add_entities(devices, True)


class PwBinarySensor(SmileGateway, BinarySensorDevice):
    """Representation of a Plugwise binary_sensor."""

    def __init__(self, api, coordinator, name, binary_sensor, dev_id, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._dev_id = dev_id
        self._model = model
        self._name = name
        self._binary_sensor = binary_sensor
        self._is_on = False

        if self._dev_id == self._api.heater_id:
            self._name = f"Auxiliary"

        bsensorname = binary_sensor.replace("_", " ").title()
        self._sensorname = f"{self._name} {bsensorname}"

        self._via_id = self._api.gateway_id
        if self._dev_id == self._api.gateway_id:
            self._name = f"Smile {self._name}"
            self._via_id = None

        self._unique_id = f"{dev_id}-{binary_sensor}"

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._sensorname

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.is_on

    @property
    def state(self):
        """Return the state of the binary sensor."""
        if self._is_on:
            return STATE_ON
        return STATE_OFF

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "model": self._model.replace("_", " ").title(),
            "via_device": (DOMAIN, self._via_id),
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._binary_sensor == "dhw_state":
            return WATER_ICON
        if self._binary_sensor == "slave_boiler_state":
            return FLAME_ICON
        if self._binary_sensor == "valve_position":
            if self._is_on:
                return VALVE_OPEN_ICON
            return VALVE_CLOSED_ICON

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        if self._binary_sensor == "valve_position":
            return DEVICE_CLASS_OPENING
        return "none"

    def _process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update binary_sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._binary_sensor)
        else:
            if self._binary_sensor in data:
                if isinstance(data[self._binary_sensor], float):
                    self._is_on = data[self._binary_sensor] == 1.0
                self._is_on = data[self._binary_sensor]

        self.async_write_ha_state()
