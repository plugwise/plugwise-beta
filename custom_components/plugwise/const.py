"""Constants for Plugwise beta component."""

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DEVICE_CLASS_OUTLET, DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_STATE,
    ATTR_UNIT_OF_MEASUREMENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TIME_MILLISECONDS,
)

API = "api"
ATTR_ENABLED_DEFAULT = "enabled_default"
DOMAIN = "plugwise"
COORDINATOR = "coordinator"
FW = "fw"
GATEWAY = "gateway"
ID = "id"
PW_CLASS = "class"
PW_LOCATION = "location"
PW_MODEL = "model"
PW_TYPE = "plugwise_type"
SCHEDULE_OFF = "false"
SCHEDULE_ON = "true"
SMILE = "smile"
STICK = "stick"
STRETCH = "stretch"
STRETCH_USERNAME = "stretch"
VENDOR = "vendor"
USB = "usb"

FLOW_NET = "Network: Smile/Stretch"
FLOW_SMILE = "Smile (Adam/Anna/P1)"
FLOW_STRETCH = "Stretch (Stretch)"
FLOW_TYPE = "flow_type"
FLOW_USB = "USB: Stick"

UNDO_UPDATE_LISTENER = "undo_update_listener"

# Default directives
DEFAULT_MAX_TEMP = 30
DEFAULT_MIN_TEMP = 4
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = {
    "power": 10,
    "stretch": 60,
    "thermostat": 60,
}
DEFAULT_TIMEOUT = 10
DEFAULT_USERNAME = "smile"

# --- Const for Plugwise Smile and Stretch
GATEWAY_PLATFORMS = [BINARY_SENSOR_DOMAIN, CLIMATE_DOMAIN, SENSOR_DOMAIN, SWITCH_DOMAIN]
SENSOR_PLATFORMS = [SENSOR_DOMAIN, SWITCH_DOMAIN]
SERVICE_DELETE = "delete_notification"

# Climate const:
MASTER_THERMOSTATS = [
    "thermostat",
    "zone_thermometer",
    "zone_thermostat",
    "thermostatic_radiator_valve",
]

# Config_flow const:
ZEROCONF_MAP = {
    "smile": "P1",
    "smile_thermo": "Anna",
    "smile_open_therm": "Adam",
    "stretch": "Stretch",
}


# --- Const for Plugwise USB-stick.

PLATFORMS_USB = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN, SWITCH_DOMAIN]
CONF_USB_PATH = "usb_path"

# Callback types
CB_NEW_NODE = "NEW_NODE"
CB_JOIN_REQUEST = "JOIN_REQUEST"

# Sensor IDs
USB_AVAILABLE_ID = "available"
USB_CURRENT_POWER_ID = "power_1s"
USB_CURRENT_POWER_8S_ID = "power_8s"
USB_ENERGY_CONSUMPTION_TODAY_ID = "energy_consumption_today"
USB_POWER_CONSUMPTION_TODAY_ID = "power_con_today"
USB_MOTION_ID = "motion"
USB_RELAY_ID = "relay"

# Sensor types
STICK_API = {
    "ping": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: "mdi:speedometer",
        ATTR_NAME: "Ping roundtrip",
        ATTR_STATE: "ping",
        ATTR_UNIT_OF_MEASUREMENT: TIME_MILLISECONDS,
    },
    USB_CURRENT_POWER_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Power usage",
        ATTR_STATE: "current_power_usage",
        ATTR_UNIT_OF_MEASUREMENT: POWER_WATT,
    },
    USB_CURRENT_POWER_8S_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: None,
        ATTR_NAME: "Power usage 8 seconds",
        ATTR_STATE: "current_power_usage_8_sec",
        ATTR_UNIT_OF_MEASUREMENT: POWER_WATT,
    },
    "power_con_cur_hour": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Power consumption current hour",
        ATTR_STATE: "power_consumption_current_hour",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    "power_con_prev_hour": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Power consumption previous hour",
        ATTR_STATE: "power_consumption_previous_hour",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    USB_ENERGY_CONSUMPTION_TODAY_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_ENERGY,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Energy consumption today",
        ATTR_STATE: "energy_consumption_today",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    USB_POWER_CONSUMPTION_TODAY_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Power consumption today",
        ATTR_STATE: "power_consumption_today",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    "power_con_yesterday": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Power consumption yesterday",
        ATTR_STATE: "power_consumption_yesterday",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    "power_prod_cur_hour": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: None,
        ATTR_NAME: "Power production current hour",
        ATTR_STATE: "power_production_current_hour",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    "power_prod_prev_hour": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: None,
        ATTR_NAME: "Power production previous hour",
        ATTR_STATE: "power_production_previous_hour",
        ATTR_UNIT_OF_MEASUREMENT: ENERGY_KILO_WATT_HOUR,
    },
    "RSSI_in": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_SIGNAL_STRENGTH,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: None,
        ATTR_NAME: "Inbound RSSI",
        ATTR_STATE: "rssi_in",
        ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    },
    "RSSI_out": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_SIGNAL_STRENGTH,
        ATTR_ENABLED_DEFAULT: False,
        ATTR_ICON: None,
        ATTR_NAME: "Outbound RSSI",
        ATTR_STATE: "rssi_out",
        ATTR_UNIT_OF_MEASUREMENT: SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    },
    USB_MOTION_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_MOTION,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Motion",
        ATTR_STATE: "motion",
        ATTR_UNIT_OF_MEASUREMENT: None,
    },
    USB_RELAY_ID: {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_OUTLET,
        ATTR_ENABLED_DEFAULT: True,
        ATTR_ICON: None,
        ATTR_NAME: "Relay state",
        ATTR_STATE: "relay_state",
        ATTR_UNIT_OF_MEASUREMENT: "state",
    },
}

ATTR_MAC_ADDRESS = "mac"

ATTR_SCAN_DAYLIGHT_MODE = "day_light"
ATTR_SCAN_SENSITIVITY_MODE = "sensitivity_mode"
ATTR_SCAN_RESET_TIMER = "reset_timer"

ATTR_SED_STAY_ACTIVE = "stay_active"
ATTR_SED_SLEEP_FOR = "sleep_for"
ATTR_SED_MAINTENANCE_INTERVAL = "maintenance_interval"
ATTR_SED_CLOCK_SYNC = "clock_sync"
ATTR_SED_CLOCK_INTERVAL = "clock_interval"

SCAN_SENSITIVITY_HIGH = "high"
SCAN_SENSITIVITY_MEDIUM = "medium"
SCAN_SENSITIVITY_OFF = "off"
SCAN_SENSITIVITY_MODES = [
    SCAN_SENSITIVITY_HIGH,
    SCAN_SENSITIVITY_MEDIUM,
    SCAN_SENSITIVITY_OFF,
]

SERVICE_CONFIGURE_BATTERY = "configure_battery_savings"
SERVICE_CONFIGURE_SCAN = "configure_scan"
SERVICE_DEVICE_ADD = "device_add"
SERVICE_DEVICE_REMOVE = "device_remove"
