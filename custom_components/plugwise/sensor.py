"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

from dataclasses import dataclass

from plugwise.constants import SensorType

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COORDINATOR,  # pw-beta
    DOMAIN,
    LOGGER,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


@dataclass
class PlugwiseSensorEntityDescription(SensorEntityDescription):
    """Describes Plugwise sensor entity."""

    key: SensorType
    state_class: str | None = SensorStateClass.MEASUREMENT


SENSORS: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key="setpoint",
        translation_key="setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="setpoint_high",
        translation_key="cooling_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="setpoint_low",
        translation_key="heating_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    PlugwiseSensorEntityDescription(
        key="temperature",
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
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
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
        key="electricity_consumed_point",
        translation_key="electricity_consumed_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
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
        key="electricity_produced_point",
        translation_key="electricity_produced_point",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
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
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    PlugwiseSensorEntityDescription(
        key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        entity_category=EntityCategory.DIAGNOSTIC,
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
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
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
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities: list[PlugwiseSensorEntity] = []
    for device_id, device in coordinator.data.devices.items():
        if not (sensors := device.get("sensors")):
            continue
        for description in SENSORS:
            if description.key not in sensors:
                continue
            entities.append(
                PlugwiseSensorEntity(
                    coordinator,
                    device_id,
                    description,
                )
            )
            LOGGER.debug(
                "Add %s %s sensor", device["name"], description.translation_key
            )

    async_add_entities(entities)


class PlugwiseSensorEntity(PlugwiseEntity, SensorEntity):
    """Represent Plugwise Sensors."""

    entity_description: PlugwiseSensorEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        coordinator.current_unique_ids.add((SENSOR_DOMAIN, self._attr_unique_id))

    @property
    def native_value(self) -> int | float:
        """Return the value reported by the sensor."""
        return self.device["sensors"][self.entity_description.key]
