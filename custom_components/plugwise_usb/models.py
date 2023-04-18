"""Models for the Plugwise USB integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityDescription

from .const import STICK, USB_MOTION_ID, USB_RELAY_ID


@dataclass
class PlugwiseRequiredKeysMixin:
    """Mixin for required keys."""

    plugwise_api: str


@dataclass
class PlugwiseEntityDescription(EntityDescription, PlugwiseRequiredKeysMixin):
    """Generic Plugwise entity description."""


@dataclass
class PlugwiseSensorEntityDescription(
    SensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise sensor entity."""

    should_poll: bool = False
    state_class: str | None = SensorStateClass.MEASUREMENT
    state_request_method: str | None = None


@dataclass
class PlugwiseSwitchEntityDescription(
    SwitchEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise switch entity."""

    should_poll: bool = False
    state_request_method: str | None = None


@dataclass
class PlugwiseBinarySensorEntityDescription(
    BinarySensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise binary sensor entity."""

    icon_off: str | None = None
    should_poll: bool = False
    state_request_method: str | None = None


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_1s",
        name="Power usage",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_request_method="current_power_usage",
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="energy_consumption_today",
        name="Energy consumption today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="energy_consumption_today",
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="ping",
        name="Ping roundtrip",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_request_method="ping",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_8s",
        name="Power usage 8 seconds",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_request_method="current_power_usage_8_sec",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="RSSI_in",
        name="Inbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_in",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="RSSI_out",
        name="Outbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_out",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_con_cur_hour",
        name="Power consumption current hour",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_prod_cur_hour",
        name="Power production current hour",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_production_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_con_today",
        name="Power consumption today",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_today",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_con_prev_hour",
        name="Power consumption previous hour",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        state_request_method="power_consumption_previous_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        plugwise_api=STICK,
        key="power_con_yesterday",
        name="Power consumption yesterday",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        state_request_method="power_consumption_yesterday",
        entity_registry_enabled_default=False,
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        plugwise_api=STICK,
        key=USB_RELAY_ID,
        device_class=SwitchDeviceClass.OUTLET,
        name="Relay state",
        state_request_method="relay_state",
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        plugwise_api=STICK,
        key=USB_MOTION_ID,
        name="Motion",
        device_class=BinarySensorDeviceClass.MOTION,
        state_request_method="motion",
    ),
)
