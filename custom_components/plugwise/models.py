"""Models for the Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.humidifier.const import ATTR_HUMIDITY
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    ILLUMINANCE,
    PERCENTAGE,
    POWER_WATT,
    PRESSURE_BAR,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
    TEMP_KELVIN,
    TIME_MILLISECONDS,
    VOLUME_CUBIC_METERS,
)
from homeassistant.helpers.entity import EntityCategory, EntityDescription

from plugwise.constants import USB as USB_ID

from .const import (
    BATTERY,
    CURRENT_TEMP,
    DEVICE_STATE,
    DHW_COMF_MODE,
    DHW_STATE,
    EL_CONSUMED,
    EL_CONSUMED_INTERVAL,
    EL_CONSUMED_OFF_PEAK_CUMULATIVE,
    EL_CONSUMED_OFF_PEAK_INTERVAL,
    EL_CONSUMED_OFF_PEAK_POINT,
    EL_CONSUMED_PEAK_CUMULATIVE,
    EL_CONSUMED_PEAK_INTERVAL,
    EL_CONSUMED_PEAK_POINT,
    EL_CONSUMED_POINT,
    EL_PRODUCED,
    EL_PRODUCED_INTERVAL,
    EL_PRODUCED_OFF_PEAK_CUMULATIVE,
    EL_PRODUCED_OFF_PEAK_INTERVAL,
    EL_PRODUCED_OFF_PEAK_POINT,
    EL_PRODUCED_PEAK_CUMULATIVE,
    EL_PRODUCED_PEAK_INTERVAL,
    EL_PRODUCED_PEAK_POINT,
    EL_PRODUCED_POINT,
    FLAME_STATE,
    GAS_CONSUMED_CUMULATIVE,
    GAS_CONSUMED_INTERVAL,
    INTENDED_BOILER_TEMP,
    LOCK,
    MOD_LEVEL,
    NET_EL_CUMULATIVE,
    NET_EL_POINT,
    OUTDOOR_TEMP,
    PW_NOTIFICATION,
    RELAY,
    RETURN_TEMP,
    SLAVE_BOILER_STATE,
    SMILE,
    STICK,
    TARGET_TEMP,
    TEMP_DIFF,
    UNIT_LUMEN,
    VALVE_POS,
    WATER_PRESSURE,
    WATER_TEMP,
)


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

    should_poll: bool = True
    state_class: str | None = SensorStateClass.MEASUREMENT
    state_request_method: str | None = None


@dataclass
class PlugwiseSwitchEntityDescription(
    SwitchEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise switch entity."""

    should_poll: bool = True
    state_request_method: str | None = None


@dataclass
class PlugwiseNumberEntityDescription(
    NumberEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise number entity."""

    min_value: float | None = 15.0
    max_value: float | None = 1440.0
    should_poll: bool = False
    step: float | None = 15.0


@dataclass
class PlugwiseBinarySensorEntityDescription(
    BinarySensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise binary sensor entity."""

    should_poll: bool = True


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key=USB_ID.power_1s,
        plugwise_api=STICK,
        name="Power usage",
        device_class=SensorDeviceClass.POWER,
        should_poll=False,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.power_8s,
        plugwise_api=STICK,
        name="Power usage 8 seconds",
        device_class=SensorDeviceClass.POWER,
        should_poll=False,
        native_unit_of_measurement=POWER_WATT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.hour_cons,
        plugwise_api=STICK,
        name="Energy consumption current hour",
        device_class=SensorDeviceClass.ENERGY,
        should_poll=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.day_cons,
        plugwise_api=STICK,
        name="Energy consumption today",
        device_class=SensorDeviceClass.ENERGY,
        should_poll=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.hour_prod,
        plugwise_api=STICK,
        name="Energy production current hour",
        device_class=SensorDeviceClass.ENERGY,
        should_poll=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.day_prod,
        plugwise_api=STICK,
        name="Energy production today",
        device_class=SensorDeviceClass.ENERGY,
        should_poll=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.ping,
        plugwise_api=STICK,
        name="Ping roundtrip",
        icon="mdi:speedometer",
        should_poll=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TIME_MILLISECONDS,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.rssi_in,
        plugwise_api=STICK,
        name="Inbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        should_poll=False,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=USB_ID.rssi_out,
        plugwise_api=STICK,
        name="Outbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        should_poll=False,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=BATTERY,
        plugwise_api=SMILE,
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key=CURRENT_TEMP,
        plugwise_api=SMILE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=DEVICE_STATE,
        plugwise_api=SMILE,
        name="Device State",
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED,
        plugwise_api=SMILE,
        name="Electricity Consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Consumed Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Consumed Off Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Consumed Off Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity Consumed Off Peak Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Consumed Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Consumed Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity Consumed Peak Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_POINT,
        plugwise_api=SMILE,
        name="Electricity Consumed Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED,
        plugwise_api=SMILE,
        name="Electricity Produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Produced Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Produced Off Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Produced Off Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity Produced Off Peak Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Produced Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Produced Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity Produced Peak Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_POINT,
        plugwise_api=SMILE,
        name="Electricity Produced Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_CUMULATIVE,
        plugwise_api=SMILE,
        name="Gas Consumed Cumulative",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=VOLUME_CUBIC_METERS,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_INTERVAL,
        plugwise_api=SMILE,
        name="Gas Consumed Interval",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=VOLUME_CUBIC_METERS,
    ),
    PlugwiseSensorEntityDescription(
        key=ATTR_HUMIDITY,
        plugwise_api=SMILE,
        name="Relative Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key=ILLUMINANCE,
        plugwise_api=SMILE,
        name="Illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=UNIT_LUMEN,
    ),
    PlugwiseSensorEntityDescription(
        key=INTENDED_BOILER_TEMP,
        plugwise_api=SMILE,
        name="Intended Boiler Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=MOD_LEVEL,
        plugwise_api=SMILE,
        name="Modulation Level",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_CUMULATIVE,
        plugwise_api=SMILE,
        name="Net Electricity Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_POINT,
        plugwise_api=SMILE,
        name="Net Electricity Point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=OUTDOOR_TEMP,
        plugwise_api=SMILE,
        name="Outdoor Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=RETURN_TEMP,
        plugwise_api=SMILE,
        name="Return Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP,
        plugwise_api=SMILE,
        name="Setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=TEMP_DIFF,
        plugwise_api=SMILE,
        name="Temperature Difference",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_KELVIN,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=VALVE_POS,
        plugwise_api=SMILE,
        name="Valve Position",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:valve",
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_PRESSURE,
        plugwise_api=SMILE,
        name="Water Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PRESSURE_BAR,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_TEMP,
        plugwise_api=SMILE,
        name="Water Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=USB_ID.relay,
        plugwise_api=STICK,
        device_class=SwitchDeviceClass.OUTLET,
        name="Relay state",
        should_poll=False,
    ),
    PlugwiseSwitchEntityDescription(
        key=DHW_COMF_MODE,
        plugwise_api=SMILE,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        name="DHW Comfort Mode",
    ),
    PlugwiseSwitchEntityDescription(
        key=LOCK,
        plugwise_api=SMILE,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        icon="mdi:lock",
        name="Lock",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSwitchEntityDescription(
        key=RELAY,
        plugwise_api=SMILE,
        device_class=SwitchDeviceClass.SWITCH,
        name="Relay",
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key=USB_ID.motion,
        plugwise_api=STICK,
        name="Motion",
        device_class=BinarySensorDeviceClass.MOTION,
        should_poll=False,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=DHW_STATE,
        plugwise_api=SMILE,
        name="DHW State",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=FLAME_STATE,
        plugwise_api=SMILE,
        name="Flame State",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=PW_NOTIFICATION,
        plugwise_api=SMILE,
        name="Plugwise Notification",
        entity_registry_enabled_default=False,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=SLAVE_BOILER_STATE,
        plugwise_api=SMILE,
        name="Slave Boiler State",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)

PW_NUMBER_TYPES: tuple[PlugwiseNumberEntityDescription, ...] = (
    PlugwiseNumberEntityDescription(
        key=USB_ID.interval_cons,
        plugwise_api=STICK,
        name="Interval consumption logs",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    PlugwiseNumberEntityDescription(
        key=USB_ID.interval_prod,
        plugwise_api=STICK,
        name="Interval production logs",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)
