"""Constants for Plugwise beta component."""

from homeassistant.components.binary_sensor import DEVICE_CLASS_MOTION
from homeassistant.components.switch import DEVICE_CLASS_OUTLET
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    PERCENTAGE,
    POWER_WATT,
    PRESSURE_BAR,
    TEMP_CELSIUS,
    TIME_MILLISECONDS,
    VOLUME_CUBIC_METERS,
)

API = "api"
ATTR_DEFAULT_ENABLED = "default_enabled"
DOMAIN = "plugwise"
COORDINATOR = "coordinator"
GATEWAY = "gateway"
PW_TYPE = "plugwise_type"
SMILE = "smile"
STICK = "stick"
STRETCH = "stretch"
USB = "usb"

FLOW_NET = "flow_network"
FLOW_TYPE = "flow_type"
FLOW_USB = "flow_usb"
FLOW_SMILE = "smile (Adam/Anna/P1)"
FLOW_STRETCH = "stretch (Stretch)"

UNDO_UPDATE_LISTENER = "undo_update_listener"

# Sensor mapping
SENSORS_DEVICE_CLASS = "class"
SENSORS_ICON = "icon"
SENSORS_UOM = "unit"

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

STRETCH_USERNAME = "stretch"

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

BINARY_SENSOR_MAP = {
    "dhw_state": ["Domestic Hot Water State", None],
    "slave_boiler_state": ["Secondary Heater Device State", None],
}

# climate const:
THERMOSTAT_CLASSES = [
    "thermostat",
    "zone_thermostat",
    "thermostatic_radiator_valve",
]

# config_flow const:
ZEROCONF_MAP = {
    "smile": "P1",
    "smile_thermo": "Anna",
    "smile_open_therm": "Adam",
    "stretch": "Stretch",
}

def temperature_sensor(name_default = "Temperature", enabled_default = True): 
    """Return standardized dict with temperature description."""
    return {
        "class": DEVICE_CLASS_TEMPERATURE,
        "enabled_default": enabled_default,
        "icon": None,
        "name": name_default,
        "unit": TEMP_CELCIUS,
    }

def energy_sensor(name_default = "Power usage", unit_default = POWER_WATT, enabled_default = True): 
    """Return standardized dict with energy description."""
    return {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": enabled_default,
        "icon": None,
        "name": name_default,
        "unit": unit_default,
    }

THERMOSTAT_SENSORS = {
    "battery": {
        "class": DEVICE_CLASS_BATTERY,
        "enabled_default": True,
        "icon": None,
        "name": "Charge",
        "unit": PERCENTAGE,
    },
    "illuminance": {
        "class": DEVICE_CLASS_ILLUMINANCE,
        "enabled_default": True,
        "icon": None,
        "name": "Illuminance",
        "unit": UNIT_LUMEN,
    },
    "outdoor_temperature": temperature_sensor(),
    "setpoint": temperature_sensor(),
    "temperature": temperature_sensor(),
    "temperature_difference": temperature_sensor(),
    "valve_position": {
        "class": None,
        "enabled_default": True,
        "icon": "mdi:valve",
        "name": "Valve position",
        "unit": PERCENTAGE,
    },
}

AUX_DEV_SENSORS = {
    "intended_boiler_temperature": temperature_sensor(),
    "modulation_level": {
        "class": None,
        "enabled_default": False,
        "icon": "mdi:percent",
        "name": "Heater Modulation Level",
        "unit": PERCENTAGE,
    },
    "return_temperature": temperature_sensor(False),
    "water_pressure": {
        "class": DEVICE_CLASS_PRESSURE,
        "enabled_default": True,
        "icon": None,
        "name": "Pressure",
        "unit": PRESSURE_BAR,
    },
    "water_temperature": temperature_sensor(),
}

ENERGY_SENSORS = {
    "electricity_consumed": energy_sensor("Current Consumed Power"), 
    "electricity_produced": energy_sensor("Current Produced Power"),
    "electricity_consumed_interval": energy_sensor("Consumed Power Interval", ENERGY_WATT_HOUR),
    "electricity_consumed_peak_interval": energy_sensor("Consumed Power Interval", ENERGY_WATT_HOUR),
    "electricity_consumed_off_peak_interval": energy_sensor("Consumed Power Interval (off peak)", ENERGY_WATT_HOUR),
    "electricity_produced_interval": energy_sensor("Produced Power Interval", ENERGY_WATT_HOUR),
    "electricity_produced_peak_interval": energy_sensor("Produced Power Interval", ENERGY_WATT_HOUR),
    "electricity_produced_off_peak_interval": energy_sensor("Produced Power Interval (off peak)", ENERGY_WATT_HOUR),
    "electricity_consumed_off_peak_point": energy_sensor("Current Consumed Power (off peak)"),
    "electricity_consumed_peak_point": energy_sensor("Current Consumed Power"),
    "electricity_consumed_off_peak_cumulative": energy_sensor("Cumulative Consumed Power (off peak)", ENERGY_KILO_WATT_HOUR),
    "electricity_consumed_peak_cumulative": energy_sensor("Cumulative Consumed Power", ENERGY_KILO_WATT_HOUR),
    "electricity_produced_off_peak_point": energy_sensor("Current Consumed Power (off peak)"),
    "electricity_produced_peak_point": energy_sensor("Current Consumed Power"),
    "electricity_produced_off_peak_cumulative": energy_sensor("Cumulative Consumed Power (off peak)", ENERGY_KILO_WATT_HOUR),
    "electricity_produced_peak_cumulative": energy_sensor("Cumulative Consumed Power", ENERGY_KILO_WATT_HOUR),
    "gas_consumed_interval": {
        "class": None,
        "enabled_default": True,
        "icon": "mdi:fire",
        "name": "Current Consumed Gas",
        "unit": VOLUME_CUBIC_METERS,
    },
    "gas_consumed_cumulative": {
        "class": None,
        "enabled_default": True,
        "icon": "mdi:fire",
        "name": "CUmulative Consumed Gas",
        "unit": VOLUME_CUBIC_METERS,
    },
    "net_electricity_point": energy_sensor("Current net Power"),
    "net_electricity_cumulative": energy_sensor("Current net Power", ENERGY_KILO_WATT_HOUR),
}

# switch const:
SWITCH_CLASSES = ["plug", "switch_group"]

# --- Const for Plugwise USB-stick.

CONF_USB_PATH = "usb_path"

# Callback types
CB_NEW_NODE = "NEW_NODE"

# Sensor IDs
AVAILABLE_SENSOR_ID = "available"
CURRENT_POWER_SENSOR_ID = "power_1s"
TODAY_ENERGY_SENSOR_ID = "power_con_today"
MOTION_SENSOR_ID = "motion"

# Sensor types
SENSORS = {
    AVAILABLE_SENSOR_ID: {
        "class": None,
        "enabled_default": False,
        "icon": "mdi:signal-off",
        "name": "Available",
        "state": "get_available",
        "unit": None,
    },
    "ping": {
        "class": None,
        "enabled_default": False,
        "icon": "mdi:speedometer",
        "name": "Ping roundtrip",
        "state": "get_ping",
        "unit": TIME_MILLISECONDS,
    },
    CURRENT_POWER_SENSOR_ID: {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": True,
        "icon": None,
        "name": "Power usage",
        "state": "get_power_usage",
        "unit": POWER_WATT,
    },
    "power_8s": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": False,
        "icon": None,
        "name": "Power usage 8 seconds",
        "state": "get_power_usage_8_sec",
        "unit": POWER_WATT,
    },
    "power_con_cur_hour": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": True,
        "icon": None,
        "name": "Power consumption current hour",
        "state": "get_power_consumption_current_hour",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    "power_con_prev_hour": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": True,
        "icon": None,
        "name": "Power consumption previous hour",
        "state": "get_power_consumption_prev_hour",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    TODAY_ENERGY_SENSOR_ID: {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": True,
        "icon": None,
        "name": "Power consumption today",
        "state": "get_power_consumption_today",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    "power_con_yesterday": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": True,
        "icon": None,
        "name": "Power consumption yesterday",
        "state": "get_power_consumption_yesterday",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    "power_prod_cur_hour": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": False,
        "icon": None,
        "name": "Power production current hour",
        "state": "get_power_production_current_hour",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    "power_prod_prev_hour": {
        "class": DEVICE_CLASS_POWER,
        "enabled_default": False,
        "icon": None,
        "name": "Power production previous hour",
        "state": "get_power_production_previous_hour",
        "unit": ENERGY_KILO_WATT_HOUR,
    },
    "RSSI_in": {
        "class": DEVICE_CLASS_SIGNAL_STRENGTH,
        "enabled_default": False,
        "icon": None,
        "name": "Inbound RSSI",
        "state": "get_in_RSSI",
        "unit": "dBm",
    },
    "RSSI_out": {
        "class": DEVICE_CLASS_SIGNAL_STRENGTH,
        "enabled_default": False,
        "icon": None,
        "name": "Outbound RSSI",
        "state": "get_out_RSSI",
        "unit": "dBm",
    },
}
BINARY_SENSORS = {
    MOTION_SENSOR_ID: {
        "class": DEVICE_CLASS_MOTION,
        "enabled_default": True,
        "icon": None,
        "name": "Motion",
        "state": "get_motion",
        "unit": None,
    }
}

# Switch types
SWITCHES = {
    "relay": {
        "class": DEVICE_CLASS_OUTLET,
        "enabled_default": True,
        "icon": None,
        "name": "Relay state",
        "state": "get_relay_state",
        "switch": "set_relay_state",
        "unit": "state",
    }
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
