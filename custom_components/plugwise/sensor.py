"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ID, ATTR_NAME, ATTR_STATE, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get_registry

from plugwise.constants import USB as USB_ID
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

# Migration list format {new:old}
MIGRATION_LIST = {
    "energy_consumption_day": "energy_consumption_today",
    "energy_consumption_hour": "power_con_cur_hour",
    "energy_production_hour": "power_prod_cur_hour",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile switches from a config entry."""
    if hass.data[DOMAIN][config_entry.entry_id][PW_TYPE] == USB:
        return await async_setup_entry_usb(hass, config_entry, async_add_entities)
    # Considered default and for earlier setups without usb/network config_flow
    return await async_setup_entry_gateway(hass, config_entry, async_add_entities)


async def async_setup_entry_usb(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
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
            # migrate old "power" entities to new "energy" entities
            # as defined in migration list
            registry = await async_get_registry(hass)
            for entity in entities:
                if MIGRATION_LIST.get(entity.entity_description.key) is not None:
                    _old_unique_id = f"{entity._node.mac}-{MIGRATION_LIST[entity.entity_description.key]}"

                    old_entity_id = registry.async_get_entity_id(
                        Platform.SENSOR, DOMAIN, _old_unique_id
                    )
                    if old_entity_id is not None:
                        _LOGGER.info(
                            "Migrate entity ID from [%s] to [%s]",
                            _old_unique_id,
                            entity.unique_id,
                        )
                        if registry.async_get_entity_id(
                            Platform.SENSOR, DOMAIN, entity.unique_id
                        ):
                            registry.async_remove(old_entity_id)
                        else:
                            registry.async_update_entity(
                                old_entity_id, new_unique_id=entity.unique_id
                            )
            async_add_entities(entities, update_before_add=True)

    for mac in hass.data[DOMAIN][config_entry.entry_id][Platform.SENSOR]:
        hass.async_create_task(async_add_sensors(mac))

    def discoved_device(mac: str):
        """Add sensors for newly discovered device."""
        hass.async_create_task(async_add_sensors(mac))

    # Listen for discovered nodes
    api_stick.subscribe_stick_callback(discoved_device, CB_NEW_NODE)


async def async_setup_entry_gateway(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile sensors from a config entry."""
    _LOGGER.debug("Plugwise hass data %s", hass.data[DOMAIN])
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []
    for dev_id in coordinator.data[1]:
        if "sensors" in coordinator.data[1][dev_id]:
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
                                    description,
                                    dev_id,
                                    data,
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
        description: PlugwiseSensorEntityDescription,
        dev_id,
        sr_data,
    ):
        """Initialise the sensor."""
        _cdata = coordinator.data[1][dev_id]
        super().__init__(
            coordinator,
            description,
            dev_id,
            _cdata.get(PW_MODEL),
            _cdata.get(ATTR_NAME),
            _cdata.get(VENDOR),
            _cdata.get(FW),
        )

        self._attr_name = f"{_cdata.get(ATTR_NAME)} {description.name}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_native_value = None
        self._attr_should_poll = description.should_poll
        self._attr_unique_id = f"{dev_id}-{description.key}"
        self._attr_state_class = description.state_class
        self._sr_data = sr_data

    @callback
    def _async_process_data(self):
        """Update the entity."""
        self._attr_native_value = self._sr_data.get(ATTR_STATE)
        if self._sr_data.get(ATTR_ID) == "device_state":
            self._attr_icon = icon_selector(self._attr_native_value, None)
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
        state_value = getattr(self._node, self.entity_description.key)
        if state_value is not None:
            return float(round(state_value, 3))
        return None
