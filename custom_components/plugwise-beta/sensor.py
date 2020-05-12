"""Plugwise Sensor component for Home Assistant."""

import logging
from typing import Dict

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    PRESSURE_BAR,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import (
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_VALVE,
    DEVICE_STATE,
    DOMAIN,
    COOL_ICON,
    FLAME_ICON,
    IDLE_ICON,
)

from . import SmileGateway


_LOGGER = logging.getLogger(__name__)

ATTR_TEMPERATURE = [
    "Temperature",
    TEMP_CELSIUS,
    DEVICE_CLASS_TEMPERATURE,
    "mdi:thermometer",
]
ATTR_BATTERY_LEVEL = ["Charge", "%", DEVICE_CLASS_BATTERY, "mdi:battery-high"]
ATTR_ILLUMINANCE = [
    "Illuminance",
    "lm",
    DEVICE_CLASS_ILLUMINANCE,
    "mdi:lightbulb-on-outline",
]
ATTR_PRESSURE = ["Pressure", PRESSURE_BAR, DEVICE_CLASS_PRESSURE, "mdi:water"]
SENSOR_MAP = {
    "setpoint": ATTR_TEMPERATURE,
    "temperature": ATTR_TEMPERATURE,
    "battery": ATTR_BATTERY_LEVEL,
    "water_pressure": ATTR_PRESSURE,
    "temperature_difference": ATTR_TEMPERATURE,
    "electricity_consumed": [
        "Current Consumed Power",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_produced": [
        "Current Produced Power",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_interval": [
        "Consumed Power Interval",
        "Wh",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_produced_interval": [
        "Produced Power Interval",
        "Wh",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "outdoor_temperature": ATTR_TEMPERATURE,
    "illuminance": ATTR_ILLUMINANCE,
    "water_temperature": ATTR_TEMPERATURE,
    "electricity_consumed_off_peak_point": [
        "Current Consumed Power (off peak)",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_peak_point": [
        "Current Consumed Power",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        "kWh",
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_consumed_peak_cumulative": [
        "Cumulative Consumed Power",
        "kWh",
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_produced_off_peak_point": [
        "Current Consumed Power (off peak)",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:white-balance-sunny",
    ],
    "electricity_produced_peak_point": [
        "Current Consumed Power",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:white-balance-sunny",
    ],
    "electricity_produced_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        "kWh",
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_produced_peak_cumulative": [
        "Cumulative Consumed Power",
        "kWh",
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "gas_consumed_interval": [
        "Current Consumed Gas",
        "m3",
        DEVICE_CLASS_GAS,
        "mdi:gas-cylinder",
    ],
    "gas_consumed_cumulative": [
        "Cumulative Consumed Gas",
        "m3",
        DEVICE_CLASS_GAS,
        "mdi:gauge",
    ],
    "net_electricity_point": [
        "Current net Power",
        "W",
        DEVICE_CLASS_POWER,
        "mdi:solar-power",
    ],
    "net_electricity_cumulative": [
        "Cumulative net Power",
        "kWh",
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "valve_position": [
        "Valve Position",
        "%",
        DEVICE_CLASS_VALVE,
        "mdi:valve",
    ],
}

INDICATE_ACTIVE_LOCAL_DEVICE = [
    "boiler_state",
    "cooling_state",
    "flame_state",
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug("Plugwise hass data %s", hass.data[DOMAIN])
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]


    _LOGGER.debug("Plugwise sensor type %s", api.smile_type)

    devices = []
    all_devices = api.get_all_devices()
    single_thermostat = api.single_master_thermostat()
    _LOGGER.debug("Plugwise all devices (not just sensor) %s", all_devices)
    for dev_id, device in all_devices.items():
        data = api.get_device_data(dev_id)
        _LOGGER.debug("Plugwise all device data (not just sensor) %s", data)
        _LOGGER.debug("Plugwise sensor Dev %s", device["name"])
        for sensor, sensor_type in SENSOR_MAP.items():
            if sensor in data:
                if data[sensor] is not None:
                    if "power" in device["types"]:
                        model = None

                        if "plug" in device["types"]:
                            model = "Metered Switch"

                        devices.append(
                            PwPowerSensor(
                                api,
                                coordinator,
                                device["name"],
                                dev_id,
                                sensor,
                                sensor_type,
                                model,
                            )
                        )
                    else:
                        devices.append(
                            PwThermostatSensor(
                                api,
                                coordinator,
                                device["name"],
                                dev_id,
                                sensor,
                                sensor_type,
                            )
                        )
                    _LOGGER.info("Added sensor.%s", device["name"])

        if single_thermostat is not None and not single_thermostat:
            idx = 1
            for state in INDICATE_ACTIVE_LOCAL_DEVICE:
                if state in data:
                    if idx == 1:
                        _LOGGER.debug("Plugwise aux sensor Dev %s", device["name"])
                        devices.append(
                            PwThermostatSensor(
                                api, coordinator, device["name"], dev_id, DEVICE_STATE, None,
                            )
                        )
                        _LOGGER.info(
                            "Added sensor.%s_state", "{}".format(device["name"])
                        )
                        idx += 1

    async_add_entities(devices, True)


class PwThermostatSensor(SmileGateway, Entity):
    """Thermostat (or generic) sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._dev_id = dev_id
        if sensor_type is not None:
            self._unit_of_measurement = sensor_type[1]
            self._device = sensor_type[2]
            self._icon = sensor_type[3]
        else:
            self._unit_of_measurement = None
            self._device = "auxiliary"
        self._name = name
        self._sensor = sensor
        self._sensor_type = sensor_type
        self._class = self._device
        self._state = None
        self._boiler_state = False
        self._heating_state = False
        self._cooling_state = False

        if self._dev_id == self._api.heater_id:
            self._name = f"Auxiliary"
        sensorname = sensor.replace("_", " ").title()
        self._sensorname = f"{self._name} {sensorname}"

        self._via_id = self._api.gateway_id
        if self._dev_id == self._api.gateway_id:
            self._name = f"Smile {self._name}"
            self._via_id = None

        self._unique_id = f"cl-{dev_id}-{self._name}-{sensor}"
        

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Device class of this entity."""
        return self._class

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._sensorname

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._via_id),
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon for the sensor."""
        if self._sensor_type is None:
            if self._boiler_state or self._heating_state:
                return FLAME_ICON
            if self._cooling_state:
                return COOL_ICON
            return IDLE_ICON
        return self._icon

    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._name)
        else:
            if self._sensor in data:
                if data[self._sensor] is not None:
                    measurement = data[self._sensor]
                    if self._sensor == "battery" or self._sensor == "valve_position":
                        measurement = measurement * 100
                    if self._unit_of_measurement == "%":
                        measurement = int(measurement)
                    self._state = measurement

            if "boiler_state" in data:
                if data["boiler_state"] is not None:
                    self._boiler_state = data["boiler_state"]
            if "heating_state" in data:
                if data["heating_state"] is not None:
                    self._heating_state = data["heating_state"]
            if "cooling_state" in data:
                if data["cooling_state"] is not None:
                    self._cooling_state = data["cooling_state"]
            if self._sensor == DEVICE_STATE:
                if self._boiler_state or self._heating_state:
                    self._state = "heating"
                elif self._cooling_state:
                    self._state = "cooling"
                else:
                    self._state = "idle"


class PwPowerSensor(SmileGateway, Entity):
    """Power sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._model = model
        self._name = name
        self._dev_id = dev_id
        self._device = sensor_type[0]
        self._unit_of_measurement = sensor_type[1]
        self._icon = sensor_type[3]
        self._class = sensor_type[2]
        self._sensor = sensor
        self._state = None
        self._unique_id = f"{dev_id}-{name}-{sensor}"

        sensorname = sensor.replace("_", " ").title()
        self._sensorname = f"{name} {sensorname}"

        self._via_id = self._api.gateway_id
        if self._dev_id == self._via_id:
            self._via_id = None
            self._name = f"Smile {self._name}"
        

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._sensorname

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_class(self):
        """Device class of this entity."""
        return self._class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "model": self._model,
            "via_device": (DOMAIN, self._via_id),
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    
    def update(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._name)
        else:
            if self._sensor in data:
                if data[self._sensor] is not None:
                    measurement = data[self._sensor]
                    if self._unit_of_measurement == "kWh":
                        measurement = int(measurement / 1000)
                    self._state = measurement