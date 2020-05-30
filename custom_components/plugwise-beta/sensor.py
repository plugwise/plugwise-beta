"""Plugwise Sensor component for Home Assistant."""

import logging

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_WATT_HOUR,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    PRESSURE_BAR,
    TEMP_CELSIUS,
)
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
    "intended_boiler_temperature": ATTR_TEMPERATURE,
    "battery": ATTR_BATTERY_LEVEL,
    "water_pressure": ATTR_PRESSURE,
    "temperature_difference": ATTR_TEMPERATURE,
    "electricity_consumed": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_produced": [
        "Current Produced Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_interval": [
        "Consumed Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_produced_interval": [
        "Produced Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "outdoor_temperature": ATTR_TEMPERATURE,
    "illuminance": ATTR_ILLUMINANCE,
    "water_temperature": ATTR_TEMPERATURE,
    "return_temperature": ATTR_TEMPERATURE,
    "electricity_consumed_off_peak_point": [
        "Current Consumed Power (off peak)",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_peak_point": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:flash",
    ],
    "electricity_consumed_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_consumed_peak_cumulative": [
        "Cumulative Consumed Power",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_produced_off_peak_point": [
        "Current Consumed Power (off peak)",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:white-balance-sunny",
    ],
    "electricity_produced_peak_point": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:white-balance-sunny",
    ],
    "electricity_produced_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "electricity_produced_peak_cumulative": [
        "Cumulative Consumed Power",
        ENERGY_KILO_WATT_HOUR,
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
        POWER_WATT,
        DEVICE_CLASS_POWER,
        "mdi:solar-power",
    ],
    "net_electricity_cumulative": [
        "Cumulative net Power",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
        "mdi:gauge",
    ],
    "valve_position": [
        "Valve Position",
        "%",
        DEVICE_CLASS_VALVE,
        "mdi:valve",
    ],
    "modulation_level": [
        "Heater Modulation Level",
        "%",
        "modulation",
        "mdi:percent",
    ],
}

INDICATE_ACTIVE_LOCAL_DEVICE = [
    "cooling_state",
    "flame_state",
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug("Plugwise hass data %s", hass.data[DOMAIN])
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]


    _LOGGER.debug("Plugwise sensor type %s", api.smile_type)

    entities = []
    all_devices = api.get_all_devices()
    single_thermostat = api.single_master_thermostat()
    _LOGGER.debug("Plugwise all devices (not just sensor) %s", all_devices)
    for dev_id, entity in all_devices.items():
        data = api.get_device_data(dev_id)
        _LOGGER.debug("Plugwise all device data (not just sensor) %s", data)
        _LOGGER.debug("Plugwise sensor Dev %s", entity["name"])
        for sensor, sensor_type in SENSOR_MAP.items():
            if sensor in data:
                if data[sensor] is None:
                    continue

                if "power" in entity["types"]:
                    model = None

                    if "plug" in entity["types"]:
                        model = "Metered Switch"

                    entities.append(
                        PwPowerSensor(
                            api,
                            coordinator,
                            entity["name"],
                            dev_id,
                            sensor,
                            sensor_type,
                            model,
                        )
                    )
                else:
                    entities.append(
                        PwThermostatSensor(
                            api,
                            coordinator,
                            entity["name"],
                            dev_id,
                            sensor,
                            sensor_type,
                        )
                    )
                _LOGGER.info("Added sensor.%s", entity["name"])

        # If not None and False (hence `is False`, not `not False`)
        if single_thermostat is False:
            for state in INDICATE_ACTIVE_LOCAL_DEVICE:
                # Once we hit this, append and break (don't add twice)
                if state in data:
                    _LOGGER.debug("Plugwise aux sensor Dev %s", entity["name"])
                    entities.append(
                        PwThermostatSensor(
                            api, coordinator, entity["name"], dev_id, DEVICE_STATE, None,
                        )
                    )
                    _LOGGER.info(
                        "Added sensor.%s_state", "{}".format(entity["name"])
                    )
                    break

    async_add_entities(entities, True)


class SmileSensor(SmileGateway):
    """Represent Smile Sensors."""

    def __init__(self, api, coordinator):
        """Initialise the sensor."""
        super().__init__(api, coordinator)

        self._dev_class = None
        self._state = None

    @property
    def device_class(self):
        """Device class of this entity."""
        if not self._dev_class:
            pass
        return self._dev_class

    @property
    def state(self):
        """Device class of this entity."""
        if not self._state:
            pass
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement


class PwThermostatSensor(SmileSensor, Entity):
    """Thermostat (or generic) sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._gateway_id = self._api.gateway_id
        self._dev_id = dev_id
        self._sensor_type = sensor_type
        self._entity_name = name
        self._sensor = sensor
        self._state = None
        self._model = None
        self._unit_of_measurement = None
        if self._sensor_type is not None:
            self._model = self._sensor_type[0]
            self._unit_of_measurement = self._sensor_type[1]
            self._dev_class = self._sensor_type[2]
            self._icon = self._sensor_type[3]
        else:
            self._dev_class = "auxiliary"

        self._heating_state = False
        self._cooling_state = False

        if self._dev_id == self._api.heater_id:
            self._entity_name = f"Auxiliary"
        sensorname = sensor.replace("_", " ").title()
        self._name = f"{self._entity_name} {sensorname}"

        if self._dev_id == self._api.gateway_id:
            self._entity_name = f"Smile {self._entity_name}"

        self._unique_id = f"cl-{dev_id}-{self._name}-{sensor}"
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    def _process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._name)
            self.async_write_ha_state()
            return
        if self._sensor in data:
            if data[self._sensor] is not None:
                measurement = data[self._sensor]
                if self._sensor == "battery" or self._sensor == "valve_position":
                    measurement = measurement * 100
                if self._unit_of_measurement == "%":
                    measurement = int(measurement)
                self._state = measurement

        if "heating_state" in data:
            if data["heating_state"] is not None:
                self._heating_state = data["heating_state"]
        if "cooling_state" in data:
            if data["cooling_state"] is not None:
                self._cooling_state = data["cooling_state"]
        if self._sensor == DEVICE_STATE:
            if self._heating_state:
                self._state = "heating"
            elif self._cooling_state:
                self._state = "cooling"
            else:
                self._state = "idle"

        if self._sensor_type is None:
            self._icon = IDLE_ICON
            if self._heating_state:
                self._icon = FLAME_ICON
            if self._cooling_state:
                self._icon = COOL_ICON

        self.async_write_ha_state()


class PwPowerSensor(SmileSensor, Entity):
    """Power sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator)

        self._api = api
        self._gateway_id = self._api.gateway_id
        self._model = model
        self._entity_name = name
        self._dev_id = dev_id
        self._device = sensor_type[0]
        self._unit_of_measurement = sensor_type[1]
        self._dev_class = sensor_type[2]
        self._icon = sensor_type[3]
        self._sensor = sensor
        self._state = None
        self._unique_id = f"{dev_id}-{name}-{sensor}"

        sensorname = sensor.replace("_", " ").title()
        self._name = f"{name} {sensorname}"

        if self._dev_id == self._api.gateway_id:
            self._entity_name = f"Smile {self._entity_name}"

    def _process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if not data:
            _LOGGER.error("Received no data for device %s.", self._name)
            self.async_write_ha_state()
            return

        if self._sensor in data:
            if data[self._sensor] is not None:
                measurement = data[self._sensor]
                if self._unit_of_measurement == ENERGY_KILO_WATT_HOUR:
                    measurement = int(measurement / 1000)
                self._state = measurement

        self.async_write_ha_state()
