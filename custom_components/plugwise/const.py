"""Constant for Plugwise beta component."""

DOMAIN = "plugwise"
COORDINATOR = "coordinator"

UNDO_UPDATE_LISTENER = "undo_update_listener"

# Sensor mapping
SENSOR_MAP_DEVICE_CLASS = 2
SENSOR_MAP_ICON = 3
SENSOR_MAP_MODEL = 0
SENSOR_MAP_UOM = 1

# Default directives
DEFAULT_MAX_TEMP = 30
DEFAULT_MIN_TEMP = 4
DEFAULT_NAME = "Smile"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = {
    "power": 10,
    "stretch": 60,
    "thermostat": 60,
}
DEFAULT_TIMEOUT = 10
DEFAULT_USERNAME = "smile"

DEVICE_CLASS_GAS = "gas"
DEVICE_CLASS_VALVE = "valve"

# Configuration directives
CONF_GAS = "gas"
CONF_MAX_TEMP = "max_temp"
CONF_MIN_TEMP = "min_temp"
CONF_THERMOSTAT = "thermostat"

DEVICE_STATE = "device_state"
UNIT_LUMEN = "lm"
SCHEDULE_OFF = "false"
SCHEDULE_ON = "true"

# Icons
COOL_ICON = "mdi:snowflake"
FLAME_ICON = "mdi:fire"
FLOW_OFF_ICON = "mdi:water-pump-off"
FLOW_ON_ICON = "mdi:water-pump"
IDLE_ICON = "mdi:circle-off-outline"
NOTIFICATION_ICON = "mdi:mailbox-up-outline"
NO_NOTIFICATION_ICON = "mdi:mailbox-outline"
SWITCH_ICON = "mdi:electric-switch"

# __init__ consts:
ALL_PLATFORMS = ["binary_sensor", "climate", "sensor", "switch"]
SERVICE_DELETE = "delete_notification"
SENSOR_PLATFORMS = ["sensor", "switch"]

# binary_sensor consts:
BINARY_SENSOR_MAP = {
    "dhw_state": ["Domestic Hot Water State", None],
    "slave_boiler_state": ["Secondary Heater Device State", None],
}

# climate consts:
THERMOSTAT_CLASSES = [
    "thermostat",
    "zone_thermostat",
    "thermostatic_radiator_valve",
]
