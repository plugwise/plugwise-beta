"""Constants for Plugwise component."""

from datetime import timedelta
import logging
from typing import Final, Literal

from homeassistant.const import Platform

# Upstream basically the whole file excluding pw-beta options

DOMAIN: Final = "plugwise"

LOGGER = logging.getLogger(__package__)

API: Final = "api"
COORDINATOR: Final = "coordinator"
CONF_HOMEKIT_EMULATION: Final = "homekit_emulation"  # pw-beta options
CONF_REFRESH_INTERVAL: Final = "refresh_interval"  # pw-beta options
CONF_MANUAL_PATH: Final = "Enter Manually"
GATEWAY: Final = "gateway"
LOCATION: Final = "location"
MAC_ADDRESS: Final = "mac_address"
REBOOT: Final = "reboot"
SMILE: Final = "smile"
STRETCH: Final = "stretch"
STRETCH_USERNAME: Final = "stretch"
UNIQUE_IDS: Final = "unique_ids"
ZIGBEE_MAC_ADDRESS: Final = "zigbee_mac_address"

# Binary Sensor constants
BINARY_SENSORS: Final = "binary_sensors"
BATTERY_STATE: Final = "low_battery"
COMPRESSOR_STATE: Final = "compressor_state"
COOLING_ENABLED: Final = "cooling_enabled"
COOLING_STATE: Final = "cooling_state"
DHW_STATE: Final = "dhw_state"
FLAME_STATE: Final = "flame_state"
HEATING_STATE: Final = "heating_state"
NOTIFICATIONS: Final ="notifications"
PLUGWISE_NOTIFICATION: Final = "plugwise_notification"
SECONDARY_BOILER_STATE: Final = "secondary_boiler_state"

# Climate constants
ACTIVE_PRESET: Final = "active_preset"
CLIMATE_MODE: Final = "climate_mode"
CONTROL_STATE: Final = "control_state"
COOLING_PRESENT: Final ="cooling_present"
DEV_CLASS: Final = "dev_class"
NONE : Final = "None"
TARGET_TEMP: Final = "setpoint"
TARGET_TEMP_HIGH: Final = "setpoint_high"
TARGET_TEMP_LOW: Final = "setpoint_low"
THERMOSTAT: Final = "thermostat"

# Config_flow constants
ANNA_WITH_ADAM: Final = "anna_with_adam"
CONTEXT: Final = "context"
FLOW_ID: Final = "flow_id"
FLOW_NET: Final = "Network: Smile/Stretch"
FLOW_SMILE: Final = "Smile (Adam/Anna/P1)"
FLOW_STRETCH: Final = "Stretch (Stretch)"
FLOW_TYPE: Final = "flow_type"
INIT: Final = "init"
PRODUCT: Final = "product"
SMILE_OPEN_THERM: Final = "smile_open_therm"
SMILE_THERMO: Final = "smile_thermo"
TITLE_PLACEHOLDERS: Final = "title_placeholders"
VERSION: Final = "version"

# Entity constants
AVAILABLE: Final = "available"
FIRMWARE: Final = "firmware"
GATEWAY_ID: Final = "gateway_id"
HARDWARE: Final = "hardware"
MODEL: Final = "model"
MODEL_ID: Final = "model_id"
SMILE_NAME: Final = "smile_name"
VENDOR: Final = "vendor"

# Number constants
MAX_BOILER_TEMP: Final = "maximum_boiler_temperature"
MAX_DHW_TEMP: Final = "max_dhw_temperature"
LOWER_BOUND: Final = "lower_bound"
RESOLUTION: Final = "resolution"
TEMPERATURE_OFFSET: Final = "temperature_offset"
UPPER_BOUND: Final = "upper_bound"

# Sensor constants
DHW_TEMP: Final = "dhw_temperature"
DHW_SETPOINT: Final = "domestic_hot_water_setpoint"
EL_CONSUMED: Final = "electricity_consumed"
EL_CONS_INTERVAL: Final = "electricity_consumed_interval"
EL_CONS_OP_CUMULATIVE: Final = "electricity_consumed_off_peak_cumulative"
EL_CONS_OP_INTERVAL: Final = "electricity_consumed_off_peak_interval"
EL_CONS_OP_POINT: Final = "electricity_consumed_off_peak_point"
EL_CONS_P_CUMULATIVE: Final = "electricity_consumed_peak_cumulative"
EL_CONS_P_INTERVAL: Final = "electricity_consumed_peak_interval"
EL_CONS_P_POINT: Final = "electricity_consumed_peak_point"
EL_CONS_POINT: Final = "electricity_consumed_point"
EL_PH1_CONSUMED: Final = "electricity_phase_one_consumed"
EL_PH2_CONSUMED: Final = "electricity_phase_two_consumed"
EL_PH3_CONSUMED: Final = "electricity_phase_three_consumed"
EL_PH1_PRODUCED: Final = "electricity_phase_one_produced"
EL_PH2_PRODUCED: Final = "electricity_phase_two_produced"
EL_PH3_PRODUCED: Final = "electricity_phase_three_produced"
EL_PRODUCED: Final = "electricity_produced"
EL_PROD_INTERVAL: Final = "electricity_produced_interval"
EL_PROD_OP_CUMULATIVE: Final = "electricity_produced_off_peak_cumulative"
EL_PROD_OP_INTERVAL: Final = "electricity_produced_off_peak_interval"
EL_PROD_OP_POINT: Final = "electricity_produced_off_peak_point"
EL_PROD_P_CUMULATIVE: Final = "electricity_produced_peak_cumulative"
EL_PROD_P_INTERVAL: Final = "electricity_produced_peak_interval"
EL_PROD_P_POINT: Final = "electricity_produced_peak_point"
EL_PROD_POINT: Final = "electricity_produced_point"
GAS_CONS_CUMULATIVE: Final = "gas_consumed_cumulative"
GAS_CONS_INTERVAL: Final = "gas_consumed_interval"
INTENDED_BOILER_TEMP: Final = "intended_boiler_temperature"
MOD_LEVEL: Final = "modulation_level"
NET_EL_POINT: Final = "net_electricity_point"
NET_EL_CUMULATIVE: Final = "net_electricity_cumulative"
OUTDOOR_AIR_TEMP: Final = "outdoor_air_temperature"
OUTDOOR_TEMP: Final = "outdoor_temperature"
RETURN_TEMP: Final = "return_temperature"
SENSORS: Final = "sensors"
SOLAR_IRRADIANCE: Final = "solar_irradiance"
TEMP_DIFF: Final = "temperature_difference"
VALVE_POS: Final = "valve_position"
VOLTAGE_PH1: Final = "voltage_phase_one"
VOLTAGE_PH2: Final = "voltage_phase_two"
VOLTAGE_PH3: Final = "voltage_phase_three"
WATER_TEMP: Final = "water_temperature"
WATER_PRESSURE: Final = "water_pressure"

# Select constants
AVAILABLE_SCHEDULES: Final = "available_schedules"
DHW_MODE: Final = "dhw_mode"
DHW_MODES: Final = "dhw_modes"
GATEWAY_MODE: Final = "gateway_mode"
GATEWAY_MODES: Final = "gateway_modes"
REGULATION_MODE: Final = "regulation_mode"
REGULATION_MODES: Final = "regulation_modes"
SELECT_DHW_MODE: Final = "select_dhw_mode"
SELECT_GATEWAY_MODE: Final = "select_gateway_mode"
SELECT_REGULATION_MODE: Final = "select_regulation_mode"
SELECT_SCHEDULE: Final = "select_schedule"

# Switch constants
DHW_CM_SWITCH: Final = "dhw_cm_switch"
LOCK: Final = "lock"
MEMBERS: Final ="members"
RELAY: Final = "relay"
COOLING_ENA_SWITCH: Final ="cooling_ena_switch"
SWITCHES: Final = "switches"

# Weather constants
CONDITION: Final ="weather_description"
HUMIDITY: Final = "humidity"
TEMPERATURE: Final ="outdoor_temperature"
WEATHER: Final = "weather"
WINDSPEED: Final ="wind_speed"
WIND_BEARING: Final ="wind_bearing"

# Default directives
DEFAULT_PORT: Final[int] = 80
DEFAULT_SCAN_INTERVAL: Final[dict[str, timedelta]] = {
    "power": timedelta(seconds=10),
    "stretch": timedelta(seconds=60),
    "thermostat": timedelta(seconds=60),
}
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_USERNAME: Final = "smile"

# --- Const for Plugwise Smile and Stretch
PLATFORMS: Final[list[str]] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WEATHER,
]
SERVICE_DELETE: Final = "delete_notification"
SEVERITIES: Final[list[str]] = ["other", "info", "message", "warning", "error"]

# Climate const:
MASTER_THERMOSTATS: Final[list[str]] = [
    "thermostat",
    "zone_thermometer",
    "zone_thermostat",
    "thermostatic_radiator_valve",
]

# Config_flow const:
ZEROCONF_MAP: Final[dict[str, str]] = {
    "smile": "Smile P1",
    "smile_thermo": "Smile Anna",
    "smile_open_therm": "Adam",
    "stretch": "Stretch",
}

type NumberType = Literal[
    "maximum_boiler_temperature",
    "max_dhw_temperature",
    "temperature_offset",
]

type SelectType = Literal[
    "select_dhw_mode",
    "select_gateway_mode",
    "select_regulation_mode",
    "select_schedule",
]
type SelectOptionsType = Literal[
    "dhw_modes",
    "gateway_modes",
    "regulation_modes",
    "available_schedules",
]
