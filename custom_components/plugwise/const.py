"""Constants for Plugwise component."""
from datetime import timedelta
import logging
from typing import Final, Literal

from homeassistant.const import Platform

DOMAIN: Final = "plugwise"

LOGGER = logging.getLogger(__package__)

API: Final = "api"
COORDINATOR: Final = "coordinator"
CONF_HOMEKIT_EMULATION: Final = "homekit_emulation"  # pw-beta options
CONF_REFRESH_INTERVAL: Final = "refresh_interval"  # pw-beta options
CONF_MANUAL_PATH: Final = "Enter Manually"
DEVICES: Final = "devices"
GATEWAY: Final = "gateway"
LOCATION: Final = "location"
MAC_ADDRESS: Final = "mac_address"
SMILE: Final = "smile"
STRETCH: Final = "stretch"
STRETCH_USERNAME: Final = "stretch"
UNDO_UPDATE_LISTENER: Final = "undo_update_listener"
UNIQUE_IDS: Final = "unique_ids"
ZIGBEE_MAC_ADDRESS: Final = "zigbee_mac_address"

# Binary Sensor constants
BINARY_SENSORS: Final = "binary_sensors"
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
CONTROL_STATE: Final = "control_state"
COOLING_PRESENT: Final ="cooling_present"
DEV_CLASS: Final = "dev_class"
NONE : Final = "None"
MODE: Final = "mode"
SETPOINT: Final = "setpoint"
SETPOINT_HIGH: Final = "setpoint_high"
SETPOINT_LOW: Final = "setpoint_low"
THERMOSTAT: Final = "thermostat"

# Config_flow constants
FLOW_NET: Final = "Network: Smile/Stretch"
FLOW_SMILE: Final = "Smile (Adam/Anna/P1)"
FLOW_STRETCH: Final = "Stretch (Stretch)"
FLOW_TYPE: Final = "flow_type"

# Entity constants
AVAILABLE: Final = "available"
FIRMWARE: Final = "firmware"
GATEWAY_ID: Final = "gateway_id"
HARDWARE: Final = "hardware"
MODEL: Final = "model"
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
SENSORS: Final = "sensors"

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

# Default directives
DEFAULT_PORT: Final = 80
DEFAULT_SCAN_INTERVAL: Final[dict[str, timedelta]] = {
    "power": timedelta(seconds=10),
    "stretch": timedelta(seconds=60),
    "thermostat": timedelta(seconds=60),
}
DEFAULT_TIMEOUT: Final = 10
DEFAULT_USERNAME: Final = "smile"

# --- Const for Plugwise Smile and Stretch
PLATFORMS: Final[list[str]] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
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

NumberType = Literal[
    "maximum_boiler_temperature",
    "max_dhw_temperature",
    "temperature_offset",
]

SelectType = Literal[
    "select_dhw_mode",
    "select_gateway_mode",
    "select_regulation_mode",
    "select_schedule",
]
SelectOptionsType = Literal[
    "dhw_modes",
    "gateway_modes",
    "regulation_modes",
    "available_schedules",
]
