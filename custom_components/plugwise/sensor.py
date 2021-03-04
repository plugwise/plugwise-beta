"""Plugwise Sensor component for Home Assistant."""

import logging

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_STATE,
)
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN

from .gateway import SmileGateway
from .usb import NodeEntity
from .const import (
    API,
    ATTR_ENABLED_DEFAULT,
    AUX_DEV_SENSORS,
    CB_NEW_NODE,
    COOL_ICON,
    COORDINATOR,
    DEVICE_STATE,
    DOMAIN,
    ENERGY_SENSORS,
    HEATING_ICON,
    IDLE_ICON,
    PW_CLASS,
    PW_MODEL,
    PW_TYPE,
    STICK,
    STICK_API,
    THERMOSTAT_SENSORS,
    USB,
    USB_AVAILABLE_ID,
    USB_MOTION_ID,
    USB_RELAY_ID,
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    _LOGGER.debug("Plugwise sensor type %s", api.smile_type)

    entities = []
    devices = api.get_all_devices()
    _LOGGER.debug("Plugwise all devices (not just sensor) %s", devices)
    for dev_id in devices:
        data = api.get_device_data(dev_id)
        _LOGGER.debug("Plugwise all device data (not just sensor) %s", data)
        _LOGGER.debug("Plugwise sensor Dev %s", devices[dev_id][ATTR_NAME])
        for sensor in ENERGY_SENSORS:
            if data.get(sensor) is None:
                continue

            entities.append(
                GWSensor(
                    api,
                    coordinator,
                    devices[dev_id][ATTR_NAME],
                    dev_id,
                    sensor,
                    ENERGY_SENSORS[sensor],
                    devices[dev_id][PW_MODEL],
                    devices[dev_id]["vendor"],
                    devices[dev_id]["fw"],
                )
            )
            _LOGGER.info("Added sensor.%s", devices[dev_id][ATTR_NAME])

        for sensor in THERMOSTAT_SENSORS:
            if data.get(sensor) is None:
                continue

            entities.append(
                GWSensor(
                    api,
                    coordinator,
                    devices[dev_id][ATTR_NAME],
                    dev_id,
                    sensor,
                    THERMOSTAT_SENSORS[sensor],
                    devices[dev_id][PW_MODEL],
                    devices[dev_id]["vendor"],
                    devices[dev_id]["fw"],
                )
            )
            _LOGGER.info("Added sensor.%s", devices[dev_id][ATTR_NAME])

        for sensor in AUX_DEV_SENSORS:
            if data.get(sensor) is None or not api.active_device_present:
                continue

            entities.append(
                GWSensor(
                    api,
                    coordinator,
                    devices[dev_id][ATTR_NAME],
                    dev_id,
                    sensor,
                    AUX_DEV_SENSORS[sensor],
                    devices[dev_id][PW_MODEL],
                    devices[dev_id]["vendor"],
                    devices[dev_id]["fw"],
                )
            )
            _LOGGER.info("Added sensor.%s", devices[dev_id][ATTR_NAME])

        # If not None and False (hence `is False`, not `not False`)
        if api.single_master_thermostat() is False:
            if devices[dev_id][PW_CLASS] == "heater_central":
                _LOGGER.debug("Plugwise aux sensor Dev %s", devices[dev_id][ATTR_NAME])
                entities.append(
                    GwAuxDeviceSensor(
                        api,
                        coordinator,
                        devices[dev_id][ATTR_NAME],
                        dev_id,
                        DEVICE_STATE,
                        devices[dev_id][PW_MODEL],
                        devices[dev_id]["vendor"],
                        devices[dev_id]["fw"],
                    )
                )
                _LOGGER.info("Added auxiliary sensor %s", devices[dev_id][ATTR_NAME])

        if not api.active_device_present:
            if devices[dev_id][PW_CLASS] == "gateway" and "heating_state" in data:
                _LOGGER.debug("Plugwise Adam sensor Dev %s", devices[dev_id][ATTR_NAME])
                entities.append(
                    GwAuxDeviceSensor(
                        api,
                        coordinator,
                        devices[dev_id][ATTR_NAME],
                        dev_id,
                        DEVICE_STATE,
                        devices[dev_id][PW_MODEL],
                        devices[dev_id]["vendor"],
                        devices[dev_id]["fw"],
                    )
                )
                _LOGGER.info("Added adam sensor %s", devices[dev_id][ATTR_NAME])

    async_add_entities(entities, True)


class SmileSensor(SmileGateway):
    """Representation of a Smile Sensor."""

    def __init__(self, api, coordinator, name, dev_id, enabled_default, sensor, model, vendor, fw):
        """Initialise the sensor."""
        super().__init__(api, coordinator, name, dev_id, model, vendor, fw)

        self._sensor = sensor

        self._dev_class = None
        self._enabled_default = enabled_default
        self._icon = None
        self._name = None
        self._state = None
        self._unit_of_measurement = None

        if dev_id == self._api.gateway_id:
            self._name = f"Smile {self._name}"

        self._unique_id = f"{dev_id}-{sensor}"

    @property
    def device_class(self):
        """Return the device class of this entity, if any."""
        return self._dev_class

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


class GWSensor(SmileSensor, Entity):
    """Representation of a Smile Gateway sensor."""

    def __init__(self, api, coordinator, name, dev_id, sensor, key, model, vendor, fw):
        """Set up the Plugwise API."""
        self._enabled_default = key[ATTR_ENABLED_DEFAULT]

        super().__init__(api, coordinator, name, dev_id, self._enabled_default, sensor, model, vendor, fw)

        self._dev_class = key[ATTR_DEVICE_CLASS]
        self._icon = None
        if not self._dev_class:
            self._icon = key[ATTR_ICON]
        self._model = model
        self._name = f"{name} {key[ATTR_NAME]}"
        self._unit_of_measurement = key[ATTR_UNIT_OF_MEASUREMENT]

    @callback
    def _async_process_data(self):
        """Update the entity."""
        # _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if self._sensor not in data:
            self.async_write_ha_state()
            return

        self._state = data[self._sensor]

        self.async_write_ha_state()


class GwAuxDeviceSensor(SmileSensor, Entity):
    """Representation of an Auxiliary Device sensor."""

    def __init__(self, api, coordinator, name, dev_id, sensor, model, vendor, fw):
        """Set up the Plugwise API."""
        self._enabled_default = True

        super().__init__(api, coordinator, name, dev_id, self._enabled_default, sensor, model, vendor, fw)

        self._cooling_state = False
        self._heating_state = False
        self._name = f"{name} Device State"

    @callback
    def _async_process_data(self):
        """Update the entity."""
        # _LOGGER.debug("Update aux dev sensor called")
        data = self._api.get_device_data(self._dev_id)

        self._heating_state = data.get("heating_state")
        self._cooling_state = data.get("cooling_state")

        self._state = CURRENT_HVAC_IDLE
        self._icon = IDLE_ICON
        if self._heating_state:
            self._state = CURRENT_HVAC_HEAT
            self._icon = HEATING_ICON
        if self._cooling_state:
            self._state = CURRENT_HVAC_COOL
            self._icon = COOL_ICON

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
