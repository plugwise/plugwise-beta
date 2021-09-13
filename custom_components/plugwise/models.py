"""Models for the Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntityDescription,
)
from homeassistant.components.switch import DEVICE_CLASS_OUTLET, SwitchEntityDescription
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TIME_MILLISECONDS,
)
from homeassistant.helpers.entity import EntityDescription

from .const import STICK, USB_MOTION_ID, USB_RELAY_ID


@dataclass
class PlugwiseRequiredKeysMixin:
    """Mixin for required keys."""

    state_request_method: str
    plugwise_api: str
    should_poll: bool = False


@dataclass
class PlugwiseEntityDescription(EntityDescription, PlugwiseRequiredKeysMixin):
    """Generic Plugwise entity description."""


@dataclass
class PlugwiseSensorEntityDescription(
    SensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise sensor entity."""


@dataclass
class PlugwiseSwitchEntityDescription(
    SwitchEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise switch entity."""


@dataclass
class PlugwiseBinarySensorEntityDescription(
    BinarySensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise binary sensor entity."""


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key="power_1s",
        plugwise_api=STICK,
        name="Power usage",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
        state_request_method="current_power_usage",
    ),
    PlugwiseSensorEntityDescription(
        key="energy_consumption_today",
        plugwise_api=STICK,
        name="Energy consumption today",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="energy_consumption_today",
    ),
    PlugwiseSensorEntityDescription(
        key="ping",
        plugwise_api=STICK,
        name="Ping roundtrip",
        icon="mdi:speedometer",
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TIME_MILLISECONDS,
        state_request_method="ping",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_8s",
        plugwise_api=STICK,
        name="Power usage 8 seconds",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
        state_request_method="current_power_usage_8_sec",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_in",
        plugwise_api=STICK,
        name="Inbound RSSI",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_in",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_out",
        plugwise_api=STICK,
        name="Outbound RSSI",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_out",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_cur_hour",
        plugwise_api=STICK,
        name="Power consumption current hour",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="power_consumption_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_prod_cur_hour",
        plugwise_api=STICK,
        name="Power production current hour",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="power_production_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_today",
        plugwise_api=STICK,
        name="Power consumption today",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="power_consumption_today",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_prev_hour",
        plugwise_api=STICK,
        name="Power consumption previous hour",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="power_consumption_previous_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_yesterday",
        plugwise_api=STICK,
        name="Power consumption yesterday",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="power_consumption_yesterday",
        entity_registry_enabled_default=False,
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=USB_RELAY_ID,
        plugwise_api=STICK,
        device_class=DEVICE_CLASS_OUTLET,
        name="Relay state",
        state_request_method="relay_state",
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key=USB_MOTION_ID,
        plugwise_api=STICK,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        state_request_method="motion",
    ),
)
