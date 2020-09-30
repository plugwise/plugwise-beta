"""Plugwise Sensor component for Home Assistant."""

import logging

from homeassistant.const import ENERGY_KILO_WATT_HOUR, PERCENTAGE
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from . import SmileGateway
from .const import (
    API,
    AUX_DEV_SENSOR_MAP,
    COOL_ICON,
    COORDINATOR,
    CUSTOM_ICONS,
    DEVICE_STATE,
    DOMAIN,
    ENERGY_SENSOR_MAP,
    FLAME_ICON,
    IDLE_ICON,
    INDICATE_ACTIVE_LOCAL_DEVICE,
    SENSOR_MAP_DEVICE_CLASS,
    SENSOR_MAP_MODEL,
    SENSOR_MAP_UOM,
    THERMOSTAT_SENSOR_MAP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug("Plugwise hass data %s", hass.data[DOMAIN])
    api = hass.data[DOMAIN][config_entry.entry_id][API]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    _LOGGER.debug("Plugwise sensor type %s", api.smile_type)

    entities = []
    all_devices = api.get_all_devices()
    single_thermostat = api.single_master_thermostat()
    _LOGGER.debug("Plugwise all devices (not just sensor) %s", all_devices)
    for dev_id, device_properties in all_devices.items():
        data = api.get_device_data(dev_id)
        _LOGGER.debug("Plugwise all device data (not just sensor) %s", data)
        _LOGGER.debug("Plugwise sensor Dev %s", device_properties["name"])
        for sensor, sensor_type in {
            **AUX_DEV_SENSOR_MAP,
            **ENERGY_SENSOR_MAP,
            **THERMOSTAT_SENSOR_MAP,
        }.items():
            if data.get(sensor) is None:
                continue

            if "power" in device_properties["types"]:
                model = None

                if "plug" in device_properties["types"]:
                    model = "Metered Switch"

                entities.append(
                    PwPowerSensor(
                        api,
                        coordinator,
                        device_properties["name"],
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
                        device_properties["name"],
                        dev_id,
                        sensor,
                        sensor_type,
                    )
                )
            _LOGGER.info("Added sensor.%s", device_properties["name"])

        # If not None and False (hence `is False`, not `not False`)
        if single_thermostat is False:
            for state in INDICATE_ACTIVE_LOCAL_DEVICE:
                # Once we hit this, append and break (don't add twice)
                if state not in data:
                    continue

                _LOGGER.debug("Plugwise aux sensor Dev %s", device_properties["name"])
                entities.append(
                    PwAuxDeviceSensor(
                        api,
                        coordinator,
                        device_properties["name"],
                        dev_id,
                        DEVICE_STATE,
                    )
                )
                _LOGGER.info("Added auxiliary sensor %s", device_properties["name"])
                break

    async_add_entities(entities, True)


class SmileSensor(SmileGateway):
    """Represent Smile Sensors."""

    def __init__(self, api, coordinator, name, dev_id, sensor):
        """Initialise the sensor."""
        super().__init__(api, coordinator, name, dev_id)

        self._sensor = sensor

        self._dev_class = None
        self._state = None
        self._icon = None
        self._unit_of_measurement = None

        if dev_id == self._api.heater_id:
            self._entity_name = "Auxiliary"

        sensorname = sensor.replace("_", " ").title()
        self._name = f"{self._entity_name} {sensorname}"

        if dev_id == self._api.gateway_id:
            self._entity_name = f"Smile {self._entity_name}"

        self._unique_id = f"{dev_id}-{sensor}"

    @property
    def device_class(self):
        """Return the device class of this entity, if any."""
        return self._dev_class

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


class PwThermostatSensor(SmileSensor, Entity):
    """Thermostat (or generic) sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id, sensor)

        self._icon = None
        self._model = sensor_type[SENSOR_MAP_MODEL]
        self._unit_of_measurement = sensor_type[SENSOR_MAP_UOM]
        self._dev_class = sensor_type[SENSOR_MAP_DEVICE_CLASS]

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if self._sensor not in data:
            self.async_write_ha_state()
            return

        measurement = data[self._sensor]
        if self._unit_of_measurement == PERCENTAGE:
            measurement = int(measurement * 100)
        self._state = measurement
        self._icon = CUSTOM_ICONS.get(self._sensor, self._icon)

        self.async_write_ha_state()


class PwAuxDeviceSensor(SmileSensor, Entity):
    """Auxiliary Device sensors."""

    def __init__(self, api, coordinator, name, dev_id, sensor):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id, sensor)

        self._cooling_state = False
        self._heating_state = False
        self._icon = None

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update aux dev sensor called")
        data = self._api.get_device_data(self._dev_id)

        if "heating_state" in data:
            self._heating_state = data["heating_state"]
        if "cooling_state" in data:
            self._cooling_state = data["cooling_state"]

        self._state = CURRENT_HVAC_IDLE
        self._icon = IDLE_ICON
        if self._heating_state:
            self._state = CURRENT_HVAC_HEAT
            self._icon = FLAME_ICON
        if self._cooling_state:
            self._state = CURRENT_HVAC_COOL
            self._icon = COOL_ICON

        self.async_write_ha_state()


class PwPowerSensor(SmileSensor, Entity):
    """Power sensor devices."""

    def __init__(self, api, coordinator, name, dev_id, sensor, sensor_type, model):
        """Set up the Plugwise API."""
        super().__init__(api, coordinator, name, dev_id, sensor)

        self._icon = None
        self._model = model
        if model is None:
            self._model = sensor_type[SENSOR_MAP_MODEL]

        self._unit_of_measurement = sensor_type[SENSOR_MAP_UOM]
        self._dev_class = sensor_type[SENSOR_MAP_DEVICE_CLASS]

        if dev_id == self._api.gateway_id:
            self._model = "P1 DSMR"

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if self._sensor not in data:
            self.async_write_ha_state()
            return

        measurement = data[self._sensor]
        if self._unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            measurement = round((measurement / 1000), 1)
        self._state = measurement
        self._icon = CUSTOM_ICONS.get(self._sensor, self._icon)

        self.async_write_ha_state()
