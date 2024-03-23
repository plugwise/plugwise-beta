"""Plugwise Sensor component for Home Assistant."""
from __future__ import annotations

from dataclasses import dataclass

from plugwise.constants import SensorType

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_NAME,
    ATTR_TEMPERATURE,
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
    CURRENT_TEMP,
    DHW_SETPOINT,
    DHW_TEMP,
    DOMAIN,
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
    GAS_CONSUMED_CUMULATIVE,
    GAS_CONSUMED_INTERVAL,
    INTENDED_BOILER_TEMP,
    LOGGER,
    MOD_LEVEL,
    NET_EL_CUMULATIVE,
    NET_EL_POINT,
    OUTDOOR_AIR_TEMP,
    OUTDOOR_TEMP,
    RETURN_TEMP,
    TARGET_TEMP_HIGH,
    TARGET_TEMP_LOW,
    TEMP_DIFF,
    V_PHASE_ONE,
    V_PHASE_THREE,
    V_PHASE_TWO,
    VALVE_POS,
    WATER_PRESSURE,
    WATER_TEMP,
)
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class PlugwiseSensorEntityDescription(SensorEntityDescription):
    """Describes Plugwise sensor entity."""

    key: SensorType


PLUGWISE_SENSORS: tuple[PlugwiseSensorEntityDescription, ...] = (
    PlugwiseSensorEntityDescription(
        key=ATTR_TEMPERATURE,
        translation_key=ATTR_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP_HIGH,
        translation_key="cooling_setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        key=TARGET_TEMP_LOW,
        translation_key="heating_setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        key=CURRENT_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=INTENDED_BOILER_TEMP,
        translation_key=INTENDED_BOILER_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=TEMP_DIFF,
        translation_key=TEMP_DIFF,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=OUTDOOR_TEMP,
        translation_key=OUTDOOR_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    PlugwiseSensorEntityDescription(
        key=OUTDOOR_AIR_TEMP,
        translation_key=OUTDOOR_AIR_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_TEMP,
        translation_key=WATER_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=RETURN_TEMP,
        translation_key=RETURN_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED,
        translation_key=EL_CONSUMED,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED,
        translation_key=EL_PRODUCED,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_INTERVAL,
        translation_key=EL_CONSUMED_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_INTERVAL,
        translation_key=EL_CONSUMED_PEAK_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_INTERVAL,
        translation_key=EL_CONSUMED_OFF_PEAK_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_INTERVAL,
        translation_key=EL_PRODUCED_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_INTERVAL,
        translation_key=EL_PRODUCED_PEAK_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_INTERVAL,
        translation_key=EL_PRODUCED_OFF_PEAK_INTERVAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_POINT,
        translation_key=EL_CONSUMED_POINT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_POINT,
        translation_key=EL_CONSUMED_OFF_PEAK_POINT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_POINT,
        translation_key=EL_CONSUMED_PEAK_POINT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_OFF_PEAK_CUMULATIVE,
        translation_key=EL_CONSUMED_OFF_PEAK_CUMULATIVE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_CONSUMED_PEAK_CUMULATIVE,
        translation_key=EL_CONSUMED_PEAK_CUMULATIVE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_POINT,
        translation_key=EL_PRODUCED_POINT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_POINT,
        translation_key=EL_PRODUCED_OFF_PEAK_POINT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_POINT,
        translation_key=EL_PRODUCED_PEAK_POINT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_OFF_PEAK_CUMULATIVE,
        translation_key=EL_PRODUCED_OFF_PEAK_CUMULATIVE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PRODUCED_PEAK_CUMULATIVE,
        translation_key=EL_PRODUCED_PEAK_CUMULATIVE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_ONE_CONSUMED,
        translation_key=EL_PHASE_ONE_CONSUMED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_TWO_CONSUMED,
        translation_key=EL_PHASE_TWO_CONSUMED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_THREE_CONSUMED,
        translation_key=EL_PHASE_THREE_CONSUMED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_ONE_PRODUCED,
        translation_key=EL_PHASE_ONE_PRODUCED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_TWO_PRODUCED,
        translation_key=EL_PHASE_TWO_PRODUCED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=EL_PHASE_THREE_PRODUCED,
        translation_key=EL_PHASE_THREE_PRODUCED,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_ONE,
        translation_key=V_PHASE_ONE,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_TWO,
        translation_key=V_PHASE_TWO,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=V_PHASE_THREE,
        translation_key=V_PHASE_THREE,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_INTERVAL,
        translation_key=GAS_CONSUMED_INTERVAL,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=GAS_CONSUMED_CUMULATIVE,
        translation_key=GAS_CONSUMED_CUMULATIVE,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_POINT,
        translation_key=NET_EL_POINT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=NET_EL_CUMULATIVE,
        translation_key=NET_EL_CUMULATIVE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    PlugwiseSensorEntityDescription(
        key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key="illuminance",
        native_unit_of_measurement=LIGHT_LUX,
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PlugwiseSensorEntityDescription(
        key=MOD_LEVEL,
        translation_key=MOD_LEVEL,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=VALVE_POS,
        translation_key=VALVE_POS,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=WATER_PRESSURE,
        translation_key=WATER_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=DHW_TEMP,
        translation_key=DHW_TEMP,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PlugwiseSensorEntityDescription(
        key=DHW_SETPOINT,
        translation_key=DHW_SETPOINT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
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
        if not (sensors := device.get(SENSORS)):
            continue
        for description in PLUGWISE_SENSORS:
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
                "Add %s %s sensor", device[ATTR_NAME], description.translation_key
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

    @property
    def native_value(self) -> int | float:
        """Return the value reported by the sensor."""
        return self.device[SENSORS][self.entity_description.key]
