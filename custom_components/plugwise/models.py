"""Models for the Plugwise integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar, overload

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
from homeassistant.helpers.entity import EntityDescription
from plugwise import DeviceData

T = TypeVar("T", bound=DeviceData)


@dataclass
class PlugwiseBaseMixin(EntityDescription, Generic[T]):
    """Mixin for Plugwise."""

    pw_key: str | None = None
    pw_lookup: str | None = "sensors"

    @overload
    def pw_get_value(self, obj: T, ret: bool = False) -> bool:
        ...

    @overload
    def pw_get_value(self, obj: T, ret: float | int = 0) -> float | int:
        ...

    def pw_get_value(self, obj: T, ret: Any = None) -> Any:
        """Return value from Plugwise device."""
        if result := obj[self.pw_lookup].get(self.pw_key):  # type: ignore [literal-required]
            return result
        if result := obj[self.pw_lookup].get(self.key):  # type: ignore [literal-required]
            return result
        return ret


@dataclass
class PlugwiseSensorEntityDescription(PlugwiseBaseMixin, SensorEntityDescription):
    """Describes Plugwise sensor entity."""

    state_class: str | None = SensorStateClass.MEASUREMENT

    def pw_get_value(self, obj: T) -> float | int:  # type: ignore [override]
        """Return value from Plugwise sensor."""
        ret: float | int = 0
        return super().pw_get_value(obj, ret)


@dataclass
class PlugwiseBinarySensorEntityDescription(
    PlugwiseBaseMixin, BinarySensorEntityDescription
):
    """Describes Plugwise binary-sensor entity."""

    pw_lookup: str = "binary_sensors"
    icon_off: str | None = None

    def pw_get_value(self, obj: T) -> bool:  # type: ignore [override]
        """Return value from Plugwise sensor."""
        ret: bool = False
        return super().pw_get_value(obj, ret)


@dataclass
class PlugwiseSwitchEntityDescription(PlugwiseBaseMixin, SwitchEntityDescription):
    """Describes Plugwise switch entity."""

    pw_lookup: str = "switches"
    ret: bool = False

    def pw_get_value(self, obj: T) -> bool:  # type: ignore [override]
        """Return value from Plugwise sensor."""
        ret: bool = False
        return super().pw_get_value(obj, ret)


PW_SENSOR_TYPES: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key="setpoint",
        translation_key="setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="cooling_setpoint",
        translation_key="cooling_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="heating_setpoint",
        translation_key="heating_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="intended_boiler_temperature",
        translation_key="intended_boiler_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="temperature_difference",
        translation_key="temperature_difference",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        icon="mdi:temperature-kelvin",
    ),
    PlugwiseSensorEntityDescription(
        key="outdoor_temperature",
        translation_key="outdoor_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key="outdoor_air_temperature",
        translation_key="outdoor_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="return_temperature",
        translation_key="return_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed",
        translation_key="electricity_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced",
        translation_key="electricity_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_registry_enabled_default=False,
    ),
    # Does not exist in Core - related to P1v2
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_point",
        translation_key="electricity_consumed_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    # Does not exist in Core
    PlugwiseSensorEntityDescription(
        key="electricity_produced_point",
        translation_key="electricity_produced_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_interval",
        translation_key="electricity_consumed_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_interval",
        translation_key="electricity_consumed_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_interval",
        translation_key="electricity_consumed_off_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_interval",
        translation_key="electricity_produced_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_interval",
        translation_key="electricity_produced_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_interval",
        translation_key="electricity_produced_off_peak_interval",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_point",
        translation_key="electricity_consumed_off_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_point",
        translation_key="electricity_consumed_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_off_peak_cumulative",
        translation_key="electricity_consumed_off_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_consumed_peak_cumulative",
        translation_key="electricity_consumed_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_point",
        translation_key="electricity_produced_off_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_point",
        translation_key="electricity_produced_peak_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_off_peak_cumulative",
        translation_key="electricity_produced_off_peak_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_produced_peak_cumulative",
        translation_key="electricity_produced_peak_cumulative",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_one_consumed",
        translation_key="electricity_phase_one_consumed",
        name="Electricity phase one consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_two_consumed",
        translation_key="electricity_phase_two_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_three_consumed",
        translation_key="electricity_phase_three_consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_one_produced",
        translation_key="electricity_phase_one_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_two_produced",
        translation_key="electricity_phase_two_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="electricity_phase_three_produced",
        translation_key="electricity_phase_three_produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_one",
        translation_key="voltage_phase_one",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_two",
        translation_key="voltage_phase_two",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="voltage_phase_three",
        translation_key="voltage_phase_three",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key="gas_consumed_interval",
        translation_key="gas_consumed_interval",
        icon="mdi:meter-gas",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    ),
    PlugwiseSensorEntityDescription(
        key="gas_consumed_cumulative",
        translation_key="gas_consumed_cumulative",
        device_class=SensorDeviceClass.GAS,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key="net_electricity_point",
        translation_key="net_electricity_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    PlugwiseSensorEntityDescription(
        key="net_electricity_cumulative",
        translation_key="net_electricity_cumulative",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key="illuminance",
        translation_key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
    ),
    PlugwiseSensorEntityDescription(
        key="modulation_level",
        translation_key="modulation_level",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
    ),
    PlugwiseSensorEntityDescription(
        key="valve_position",
        translation_key="valve_position",
        icon="mdi:valve",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key="water_pressure",
        translation_key="water_pressure",
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfPressure.BAR,
    ),
    PlugwiseSensorEntityDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        pw_key="humidity",
    ),
    PlugwiseSensorEntityDescription(
        key="dhw_temperature",
        translation_key="dhw_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="domestic_hot_water_setpoint",
        translation_key="domestic_hot_water_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="maximum_boiler_temperature",
        translation_key="maximum_boiler_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        pw_key="setpoint",
        pw_lookup="maximum_boiler_temperature",
    ),
)

PW_SWITCH_TYPES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key="dhw_cm_switch",
        translation_key="dhw_cm_switch",
        icon="mdi:water-plus",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key="lock",
        translation_key="lock",
        icon="mdi:lock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key="relay",
        translation_key="relay",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    PlugwiseSwitchEntityDescription(
        key="cooling_enabled",
        translation_key="cooling_enabled",
        icon="mdi:snowflake-thermometer",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        pw_key="cooling_ena_switch",
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
