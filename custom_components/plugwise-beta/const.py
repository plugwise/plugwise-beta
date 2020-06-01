"""Constant for Plugwise beta component."""

DOMAIN = "plugwise-beta"

# Sensor mapping
SENSOR_MAP_MODEL = 0
SENSOR_MAP_UOM = 1
SENSOR_MAP_DEVICE_CLASS = 2
SENSOR_MAP_ICON = 3

# Default directives
DEFAULT_NAME = "Smile"
DEFAULT_USERNAME = "smile"
DEFAULT_TIMEOUT = 10
DEFAULT_PORT = 80
DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 30
DEFAULT_SCAN_INTERVAL = {"thermostat": 60, "power": 10}

DEVICE_CLASS_GAS = "gas"
DEVICE_CLASS_VALVE = "valve"

# Configuration directives
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_THERMOSTAT = "thermostat"
CONF_POWER = "power"
CONF_HEATER = "heater"
CONF_SOLAR = "solar"
CONF_GAS = "gas"

CURRENT_HVAC_DHW = "hot_water"
DEVICE_STATE = "device_state"
UNIT_LUMEN  = "lm"

SCHEDULE_ON = "true"
SCHEDULE_OFF = "false"

# Icons
SWITCH_ICON = "mdi:electric-switch"
FLAME_ICON = "mdi:fire"
IDLE_ICON = "mdi:circle-off-outline"
GAS_ICON = "mdi:fire"
POWER_ICON = "mdi:flash"
POWER_FAILURE_ICON = "mdi:flash-off"
SWELL_SAG_ICON = "mdi:pulse"
FLOW_OFF_ICON = "mdi:water-pump-off"
FLOW_ON_ICON = "mdi:water-pump"
