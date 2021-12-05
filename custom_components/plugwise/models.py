"""Models for the Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.humidifier.const import ATTR_HUMIDITY
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
    SensorDeviceClass,
    SensorEntityDescription,
)
from homeassistant.components.switch import (
    DEVICE_CLASS_OUTLET,
    DEVICE_CLASS_SWITCH,
    SwitchEntityDescription,
)
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    ENTITY_CATEGORY_CONFIG,
    ENTITY_CATEGORY_DIAGNOSTIC,
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
from homeassistant.helpers.entity import EntityDescription

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
    USB_MOTION_ID,
    USB_RELAY_ID,
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
    state_class: str | None = STATE_CLASS_MEASUREMENT
    state_request_method: str | None = None


@dataclass
class PlugwiseSwitchEntityDescription(
    SwitchEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise switch entity."""

    should_poll: bool = True
    state_request_method: str | None = None


@dataclass
class PlugwiseBinarySensorEntityDescription(
    BinarySensorEntityDescription, PlugwiseEntityDescription
):
    """Describes Plugwise binary sensor entity."""

    should_poll: bool = True
    state_request_method: str | None = None


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key="power_1s",
        plugwise_api=STICK,
        name="Power usage",
        device_class=SensorDeviceClass.POWER,
        should_poll=False,
        native_unit_of_measurement=POWER_WATT,
        state_request_method="current_power_usage",
    ),
    PlugwiseSensorEntityDescription(
        key="energy_consumption_today",
        plugwise_api=STICK,
        name="Energy consumption today",
        device_class=SensorDeviceClass.ENERGY,
        should_poll=False,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="energy_consumption_today",
    ),
    PlugwiseSensorEntityDescription(
        key="ping",
        plugwise_api=STICK,
        name="Ping roundtrip",
        icon="mdi:speedometer",
        should_poll=False,
        native_unit_of_measurement=TIME_MILLISECONDS,
        state_request_method="ping",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_8s",
        plugwise_api=STICK,
        name="Power usage 8 seconds",
        device_class=SensorDeviceClass.POWER,
        should_poll=False,
        native_unit_of_measurement=POWER_WATT,
        state_request_method="current_power_usage_8_sec",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_in",
        plugwise_api=STICK,
        name="Inbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        should_poll=False,
        state_request_method="rssi_in",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_out",
        plugwise_api=STICK,
        name="Outbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        should_poll=False,
        state_request_method="rssi_out",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_cur_hour",
        plugwise_api=STICK,
        name="Power consumption current hour",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        should_poll=False,
        state_request_method="power_consumption_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_prod_cur_hour",
        plugwise_api=STICK,
        name="Power production current hour",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        should_poll=False,
        state_request_method="power_production_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_today",
        plugwise_api=STICK,
        name="Power consumption today",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        should_poll=False,
        state_request_method="power_consumption_today",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_prev_hour",
        plugwise_api=STICK,
        name="Power consumption previous hour",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        should_poll=False,
        state_request_method="power_consumption_previous_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_yesterday",
        plugwise_api=STICK,
        name="Power consumption yesterday",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        should_poll=False,
        state_request_method="power_consumption_yesterday",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=BATTERY,
        plugwise_api=SMILE,
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key=CURRENT_TEMP,
        plugwise_api=SMILE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
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
        state_class=STATE_CLASS_TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Consumed Off Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Consumed Off Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL,
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
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Consumed Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL,
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
        state_class=STATE_CLASS_TOTAL,
        native_unit_of_measurement=ENERGY_WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity Produced Off Peak Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Produced Off Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL,
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
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity Produced Peak Interval",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL,
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
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=VOLUME_CUBIC_METERS,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_INTERVAL,
        plugwise_api=SMILE,
        name="Gas Consumed Interval",
        device_class=SensorDeviceClass.GAS,
        state_class=STATE_CLASS_TOTAL,
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
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=MOD_LEVEL,
        plugwise_api=SMILE,
        name="Modulation Level",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_CUMULATIVE,
        plugwise_api=SMILE,
        name="Net Electricity Cumulative",
        device_class=SensorDeviceClass.ENERGY,
        state_class=STATE_CLASS_TOTAL,
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
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP,
        plugwise_api=SMILE,
        name="Setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=TEMP_DIFF,
        plugwise_api=SMILE,
        name="Temperature Difference",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=TEMP_KELVIN,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=VALVE_POS,
        plugwise_api=SMILE,
        name="Valve Position",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:valve",
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_PRESSURE,
        plugwise_api=SMILE,
        name="Water Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=PRESSURE_BAR,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_TEMP,
        plugwise_api=SMILE,
        name="Water Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=USB_RELAY_ID,
        plugwise_api=STICK,
        device_class=DEVICE_CLASS_OUTLET,
        name="Relay state",
        should_poll=False,
        state_request_method="relay_state",
    ),
    PlugwiseSwitchEntityDescription(
        key=DHW_COMF_MODE,
        plugwise_api=SMILE,
        device_class=DEVICE_CLASS_SWITCH,
        entity_category=ENTITY_CATEGORY_CONFIG,
        name="DHW Comfort Mode",
    ),
    PlugwiseSwitchEntityDescription(
        key=LOCK,
        plugwise_api=SMILE,
        device_class=DEVICE_CLASS_SWITCH,
        entity_category=ENTITY_CATEGORY_CONFIG,
        icon="mdi:lock",
        name="Lock",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSwitchEntityDescription(
        key=RELAY,
        plugwise_api=SMILE,
        device_class=DEVICE_CLASS_SWITCH,
        name="Relay",
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key=USB_MOTION_ID,
        plugwise_api=STICK,
        name="Motion",
        device_class=BinarySensorDeviceClass.MOTION,
        should_poll=False,
        state_request_method="motion",
    ),
    PlugwiseBinarySensorEntityDescription(
        key=DHW_STATE,
        plugwise_api=SMILE,
        name="DHW State",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=FLAME_STATE,
        plugwise_api=SMILE,
        name="Flame State",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
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
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)
