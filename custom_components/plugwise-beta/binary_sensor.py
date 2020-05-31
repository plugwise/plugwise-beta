"""Plugwise Binary Sensor component for Home Assistant."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback

from .const import DOMAIN
from .sensor import SmileSensor

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

    entities = []
    binary_sensor_classes = [
        "heater_central",
        "thermo_sensor",
        "thermostatic_radiator_valve",
    ]

    all_devices = api.get_all_devices()
    for dev_id, device_properties in all_devices.items():
        if device_properties["class"] in binary_sensor_classes:
            _LOGGER.debug("Plugwise device_class %s found", device_properties["class"])
            data = api.get_device_data(dev_id)
            for binary_sensor in BINARY_SENSOR_LIST:
                _LOGGER.debug("Binary_sensor: %s", binary_sensor)
                if binary_sensor in data:
                    _LOGGER.debug(
                        "Plugwise binary_sensor Dev %s", device_properties["name"]
                    )
                    entities.append(
                        PwBinarySensor(
                            api,
                            coordinator,
                            device_properties["name"],
                            binary_sensor,
                            dev_id,
                            device_properties["class"],
                        )
                    )
                    _LOGGER.info("Added binary_sensor.%s", device_properties["name"])

    async_add_entities(entities, True)


class PwBinarySensor(SmileSensor, BinarySensorEntity):
    """Representation of a Plugwise binary_sensor."""

    def __init__(self, api, coordinator, name, binary_sensor, dev_id, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._dev_id = dev_id
        self._entity_name = name
        self._binary_sensor = binary_sensor

        self._is_on = False

        if self._dev_id == self._api.heater_id:
            self._entity_name = "Auxiliary"

        bsensorname = binary_sensor.replace("_", " ").title()
        self._name = f"{self._entity_name} {bsensorname}"

        if self._dev_id == self._api.gateway_id:
            self._entity_name = f"Smile {self._name}"

        self._unique_id = f"bs-{dev_id}-{self._entity_name}-{binary_sensor}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.is_on

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update binary_sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._binary_sensor)
            self.async_write_ha_state()
            return

        if self._binary_sensor in data:

            if isinstance(data[self._binary_sensor], float):
                self._is_on = data[self._binary_sensor] == 1.0
            self._is_on = data[self._binary_sensor]

            self._state = STATE_OFF
            if self._is_on:
                self._state = STATE_ON

        self.async_write_ha_state()
