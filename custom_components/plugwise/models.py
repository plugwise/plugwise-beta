"""Models for the Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.humidifier.const import ATTR_HUMIDITY
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    ILLUMINANCE,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.helpers.entity import EntityDescription

from .const import (
    BATTERY,
    COMPRESSOR_STATE,
    COOLING,
    COOLING_ENABLED,
    CURRENT_TEMP,
    DHW_COMF_MODE,
    DHW_STATE,
    DHW_TEMP,
    EL_CONSUMED,
    EL_CONSUMED_INTERVAL,
    EL_CONSUMED_OFF_PEAK_CUMULATIVE,
    EL_CONSUMED_OFF_PEAK_INTERVAL,
    EL_CONSUMED_OFF_PEAK_POINT,
    EL_CONSUMED_PEAK_CUMULATIVE,
    EL_CONSUMED_PEAK_INTERVAL,
    EL_CONSUMED_PEAK_POINT,
    EL_CONSUMED_POINT,
    EL_PHASE_ONE_CONSUMED,
    EL_PHASE_ONE_PRODUCED,
    EL_PHASE_THREE_CONSUMED,
    EL_PHASE_THREE_PRODUCED,
    EL_PHASE_TWO_CONSUMED,
    EL_PHASE_TWO_PRODUCED,
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
    OUTDOOR_AIR_TEMP,
    OUTDOOR_TEMP,
    PW_NOTIFICATION,
    RELAY,
    RETURN_TEMP,
    SLAVE_BOILER_STATE,
    SMILE,
    STICK,
    TARGET_TEMP,
    TARGET_TEMP_HIGH,
    TARGET_TEMP_LOW,
    TEMP_DIFF,
    USB_MOTION_ID,
    USB_RELAY_ID,
    V_PHASE_ONE,
    V_PHASE_THREE,
    V_PHASE_TWO,
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
        key="power_1s",
        plugwise_api=STICK,
        name="Power usage",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_request_method="current_power_usage",
    ),
    PlugwiseSensorEntityDescription(
        key="energy_consumption_today",
        plugwise_api=STICK,
        name="Energy consumption today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="energy_consumption_today",
    ),
    PlugwiseSensorEntityDescription(
        key="ping",
        plugwise_api=STICK,
        name="Ping roundtrip",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_request_method="ping",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_8s",
        plugwise_api=STICK,
        name="Power usage 8 seconds",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_request_method="current_power_usage_8_sec",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_in",
        plugwise_api=STICK,
        name="Inbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_in",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="RSSI_out",
        plugwise_api=STICK,
        name="Outbound RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_request_method="rssi_out",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_cur_hour",
        plugwise_api=STICK,
        name="Power consumption current hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_prod_cur_hour",
        plugwise_api=STICK,
        name="Power production current hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_production_current_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_today",
        plugwise_api=STICK,
        name="Power consumption today",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_today",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_prev_hour",
        plugwise_api=STICK,
        name="Power consumption previous hour",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_previous_hour",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="power_con_yesterday",
        plugwise_api=STICK,
        name="Power consumption yesterday",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_request_method="power_consumption_yesterday",
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP,
        plugwise_api=SMILE,
        name="Setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP_HIGH,
        plugwise_api=SMILE,
        name="Cooling setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP_LOW,
        plugwise_api=SMILE,
        name="Heating setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=CURRENT_TEMP,
        plugwise_api=SMILE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=INTENDED_BOILER_TEMP,
        plugwise_api=SMILE,
        name="Intended boiler temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=TEMP_DIFF,
        plugwise_api=SMILE,
        name="Temperature difference",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        icon="mdi:temperature-kelvin",
    ),
    PlugwiseSensorEntityDescription(
        key=OUTDOOR_TEMP,
        plugwise_api=SMILE,
        name="Outdoor temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key=OUTDOOR_AIR_TEMP,
        plugwise_api=SMILE,
        name="Outdoor air temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_TEMP,
        plugwise_api=SMILE,
        name="Water temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=RETURN_TEMP,
        plugwise_api=SMILE,
        name="Return temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED,
        plugwise_api=SMILE,
        name="Electricity consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED,
        plugwise_api=SMILE,
        name="Electricity produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_registry_enabled_default=False,
    ),
    # Does not exist in Core - related to P1v2
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_POINT,
        plugwise_api=SMILE,
        name="Electricity consumed point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    # Does not exist in Core
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_POINT,
        plugwise_api=SMILE,
        name="Electricity produced point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity consumed interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity consumed peak interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity consumed off peak interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity produced interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity produced peak interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_INTERVAL,
        plugwise_api=SMILE,
        name="Electricity produced off peak interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity consumed off peak point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity consumed peak point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity consumed off peak cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity consumed peak cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity produced off peak point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_POINT,
        plugwise_api=SMILE,
        name="Electricity produced peak point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity produced off peak cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_CUMULATIVE,
        plugwise_api=SMILE,
        name="Electricity produced peak cumulative",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_ONE_CONSUMED,
        plugwise_api=SMILE,
        name="Electricity phase one consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_TWO_CONSUMED,
        plugwise_api=SMILE,
        name="Electricity phase two consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_THREE_CONSUMED,
        plugwise_api=SMILE,
        name="Electricity phase three consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_ONE_PRODUCED,
        plugwise_api=SMILE,
        name="Electricity phase one produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_TWO_PRODUCED,
        plugwise_api=SMILE,
        name="Electricity phase two produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_THREE_PRODUCED,
        plugwise_api=SMILE,
        name="Electricity phase three produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_ONE,
        plugwise_api=SMILE,
        name="Voltage phase one",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_TWO,
        plugwise_api=SMILE,
        name="Voltage phase two",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_THREE,
        plugwise_api=SMILE,
        name="Voltage phase three",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_INTERVAL,
        plugwise_api=SMILE,
        name="Gas consumed interval",
        icon="mdi:meter-gas",
        native_unit_of_measurement=f"{UnitOfVolume.CUBIC_METERS}/{UnitOfTime.HOURS}",
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_CUMULATIVE,
        plugwise_api=SMILE,
        name="Gas consumed cumulative",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_POINT,
        plugwise_api=SMILE,
        name="Net electricity point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_CUMULATIVE,
        plugwise_api=SMILE,
        name="Net electricity cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
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
        key=ILLUMINANCE,
        plugwise_api=SMILE,
        name="Illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
    ),
    PlugwiseSensorEntityDescription(
        key=MOD_LEVEL,
        plugwise_api=SMILE,
        name="Modulation level",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
    ),
    PlugwiseSensorEntityDescription(
        key=VALVE_POS,
        plugwise_api=SMILE,
        name="Valve position",
        icon="mdi:valve",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_PRESSURE,
        plugwise_api=SMILE,
        name="Water pressure",
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfPressure.BAR,
    ),
    PlugwiseSensorEntityDescription(
        key=ATTR_HUMIDITY,
        plugwise_api=SMILE,
        name="Relative humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key=DHW_TEMP,
        plugwise_api=SMILE,
        name="DHW temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="domestic_hot_water_setpoint",
        plugwise_api=SMILE,
        name="DHW setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="maximum_boiler_temperature",
        plugwise_api=SMILE,
        name="Maximum boiler temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=USB_RELAY_ID,
        plugwise_api=STICK,
        device_class=SwitchDeviceClass.OUTLET,
        name="Relay state",
        state_request_method="relay_state",
    ),
    PlugwiseSwitchEntityDescription(
        key=DHW_COMF_MODE,
        plugwise_api=SMILE,
        name="DHW comfort mode",
        icon="mdi:water-plus",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=LOCK,
        plugwise_api=SMILE,
        name="Lock",
        icon="mdi:lock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=RELAY,
        plugwise_api=SMILE,
        name="Relay",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    PlugwiseSwitchEntityDescription(
        key=COOLING_ENABLED,
        plugwise_api=SMILE,
        name="Cooling",
        icon="mdi:snowflake-thermometer",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key=USB_MOTION_ID,
        plugwise_api=STICK,
        name="Motion",
        device_class=BinarySensorDeviceClass.MOTION,
        state_request_method="motion",
    ),
    PlugwiseBinarySensorEntityDescription(
        key=COMPRESSOR_STATE,
        plugwise_api=SMILE,
        name="Compressor state",
        icon="mdi:hvac",
        icon_off="mdi:hvac-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=COOLING,
        plugwise_api=SMILE,
        name="Cooling enabled",
        icon="mdi:snowflake-thermometer",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=DHW_STATE,
        plugwise_api=SMILE,
        name="DHW state",
        icon="mdi:water-pump",
        icon_off="mdi:water-pump-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=FLAME_STATE,
        plugwise_api=SMILE,
        name="Flame state",
        icon="mdi:fire",
        icon_off="mdi:fire-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="heating_state",
        plugwise_api=SMILE,
        name="Heating",
        icon="mdi:radiator",
        icon_off="mdi:radiator-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="cooling_state",
        plugwise_api=SMILE,
        name="Cooling",
        icon="mdi:snowflake",
        icon_off="mdi:snowflake-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=SLAVE_BOILER_STATE,
        plugwise_api=SMILE,
        name="Secondary boiler state",
        icon="mdi:fire",
        icon_off="mdi:circle-off-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key=PW_NOTIFICATION,
        plugwise_api=SMILE,
        icon="mdi:mailbox-up-outline",
        icon_off="mdi:mailbox-outline",
        name="Plugwise notification",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
