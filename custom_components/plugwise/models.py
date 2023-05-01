"""Models for the Plugwise integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntityDescription
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from plugwise import DeviceData


@dataclass
class PlugwiseSensorBaseMixin:
    """Mixin for required Plugwise sensor base description keys."""

    value_fn: Callable[[DeviceData], float | int]


@dataclass
class PlugwiseSwitchBaseMixin:
    """Mixin for required Plugwise switch base description keys."""

    value_fn: Callable[[DeviceData], bool]


@dataclass
class PlugwiseSensorEntityDescription(SensorEntityDescription, PlugwiseSensorBaseMixin):
    """Describes Plugwise sensor entity."""

    state_class: str | None = SensorStateClass.MEASUREMENT


@dataclass
class PlugwiseSwitchEntityDescription(SwitchEntityDescription, PlugwiseSwitchBaseMixin):
    """Describes Plugwise switch entity."""


@dataclass
class PlugwiseBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Plugwise binary sensor entity."""

    icon_off: str | None = None


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key="setpoint",
        translation_key="setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["setpoint"],
    ),
    PlugwiseSensorEntityDescription(
        key="cooling_setpoint",
        translation_key="cooling_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["setpoint_high"],
    ),
    PlugwiseSensorEntityDescription(
        key="heating_setpoint",
        translation_key="heating_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["setpoint_low"],
    ),
    PlugwiseSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["temperature"],
    ),
    PlugwiseSensorEntityDescription(
        key="intended_boiler_temperature",
        translation_key="intended_boiler_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["intended_boiler_temperature"],
    ),
    PlugwiseSensorEntityDescription(
        key="temperature_difference",
        translation_key="temperature_difference",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        value_fn=lambda data: data["sensors"]["temperature_difference"],
        icon="mdi:temperature-kelvin",
    ),
    PlugwiseSensorEntityDescription(
        key="outdoor_temperature",
        translation_key="outdoor_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["outdoor_temperature"],
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key="outdoor_air_temperature",
        translation_key="outdoor_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["outdoor_air_temperature"],
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["water_temperature"],
    ),
    PlugwiseSensorEntityDescription(
        key="return_temperature",
        translation_key="return_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["return_temperature"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed",
        translation_key="electricity_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_consumed"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced",
        translation_key="electricity_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_produced"],
        entity_registry_enabled_default=False,
    ),
    # Does not exist in Core - related to P1v2
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_point",
        translation_key="electricity_consumed_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_consumed_point"],
    ),
    # Does not exist in Core
    PlugwiseSensorEntityDescription(
        key="electricity_produced_point",
        translation_key="electricity_produced_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_produced_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_interval",
        translation_key="electricity_consumed_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_consumed_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_interval",
        translation_key="electricity_consumed_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_consumed_peak_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_interval",
        translation_key="electricity_consumed_off_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_consumed_off_peak_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_interval",
        translation_key="electricity_produced_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_produced_interval"],
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_interval",
        translation_key="electricity_produced_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_produced_peak_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_interval",
        translation_key="electricity_produced_off_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_produced_off_peak_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_point",
        translation_key="electricity_consumed_off_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_consumed_off_peak_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_point",
        translation_key="electricity_consumed_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_consumed_peak_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_cumulative",
        translation_key="electricity_consumed_off_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data["sensors"][
            "electricity_consumed_off_peak_cumulative"
        ],
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_cumulative",
        translation_key="electricity_consumed_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_consumed_peak_cumulative"],
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_point",
        translation_key="electricity_produced_off_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_produced_off_peak_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_point",
        translation_key="electricity_produced_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_produced_peak_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_cumulative",
        translation_key="electricity_produced_off_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data["sensors"][
            "electricity_produced_off_peak_cumulative"
        ],
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_cumulative",
        translation_key="electricity_produced_peak_cumulative",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data["sensors"]["electricity_produced_peak_cumulative"],
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_one_consumed",
        translation_key="electricity_phase_one_consumed",
        name="Electricity phase one consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_one_consumed"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_two_consumed",
        translation_key="electricity_phase_two_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_two_consumed"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_three_consumed",
        translation_key="electricity_phase_three_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_three_consumed"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_one_produced",
        translation_key="electricity_phase_one_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_one_produced"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_two_produced",
        translation_key="electricity_phase_two_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_two_produced"],
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_three_produced",
        translation_key="electricity_phase_three_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["electricity_phase_three_produced"],
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_one",
        translation_key="voltage_phase_one",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda data: data["sensors"]["voltage_phase_one"],
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_two",
        translation_key="voltage_phase_two",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda data: data["sensors"]["voltage_phase_two"],
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_three",
        translation_key="voltage_phase_three",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda data: data["sensors"]["voltage_phase_three"],
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="gas_consumed_interval",
        translation_key="gas_consumed_interval",
        icon="mdi:meter-gas",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        value_fn=lambda data: data["sensors"]["gas_consumed_interval"],
    ),
    PlugwiseSensorEntityDescription(
        key="gas_consumed_cumulative",
        translation_key="gas_consumed_cumulative",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        value_fn=lambda data: data["sensors"]["gas_consumed_cumulative"],
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="net_electricity_point",
        translation_key="net_electricity_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data["sensors"]["net_electricity_point"],
    ),
    PlugwiseSensorEntityDescription(
        key="net_electricity_cumulative",
        translation_key="net_electricity_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data["sensors"]["net_electricity_cumulative"],
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data["sensors"]["battery"],
    ),
    PlugwiseSensorEntityDescription(
        key="illuminance",
        translation_key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        value_fn=lambda data: data["sensors"]["illuminance"],
    ),
    PlugwiseSensorEntityDescription(
        key="modulation_level",
        translation_key="modulation_level",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data["sensors"]["modulation_level"],
        icon="mdi:percent",
    ),
    PlugwiseSensorEntityDescription(
        key="valve_position",
        translation_key="valve_position",
        icon="mdi:valve",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data["sensors"]["valve_position"],
    ),
    PlugwiseSensorEntityDescription(
        key="water_pressure",
        translation_key="water_pressure",
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfPressure.BAR,
        value_fn=lambda data: data["sensors"]["water_pressure"],
    ),
    PlugwiseSensorEntityDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data["sensors"]["humidity"],
    ),
    PlugwiseSensorEntityDescription(
        key="dhw_temperature",
        translation_key="dhw_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["dhw_temperature"],
    ),
    PlugwiseSensorEntityDescription(
        key="domestic_hot_water_setpoint",
        translation_key="domestic_hot_water_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["domestic_hot_water_setpoint"],
    ),
    PlugwiseSensorEntityDescription(
        key="maximum_boiler_temperature",
        translation_key="maximum_boiler_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data["sensors"]["maximum_boiler_temperature"],
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key="dhw_cm_switch",
        translation_key="dhw_cm_switch",
        icon="mdi:water-plus",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data["switches"]["dhw_cm_switch"],
    ),
    PlugwiseSwitchEntityDescription(
        key="lock",
        translation_key="lock",
        icon="mdi:lock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data["switches"]["lock"],
    ),
    PlugwiseSwitchEntityDescription(
        key="relay",
        translation_key="relay",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda data: data["switches"]["relay"],
    ),
    PlugwiseSwitchEntityDescription(
        key="cooling_enabled",
        translation_key="cooling_enabled",
        icon="mdi:snowflake-thermometer",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data["switches"]["cooling_ena_switch"],
    ),
)

PW_BINARY_SENSOR_TYPES: tuple[PlugwiseBinarySensorEntityDescription, ...] = (
    PlugwiseBinarySensorEntityDescription(
        key="compressor_state",
        translation_key="compressor_state",
        icon="mdi:hvac",
        icon_off="mdi:hvac-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="cooling_enabled",
        translation_key="cooling_enabled",
        icon="mdi:snowflake-thermometer",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="dhw_state",
        translation_key="dhw_state",
        icon="mdi:water-pump",
        icon_off="mdi:water-pump-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="flame_state",
        translation_key="flame_state",
        icon="mdi:fire",
        icon_off="mdi:fire-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="heating_state",
        translation_key="heating_state",
        icon="mdi:radiator",
        icon_off="mdi:radiator-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="cooling_state",
        translation_key="cooling_state",
        icon="mdi:snowflake",
        icon_off="mdi:snowflake-off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="slave_boiler_state",
        translation_key="slave_boiler_state",
        icon="mdi:fire",
        icon_off="mdi:circle-off-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseBinarySensorEntityDescription(
        key="plugwise_notification",
        translation_key="plugwise_notification",
        icon="mdi:mailbox-up-outline",
        icon_off="mdi:mailbox-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
