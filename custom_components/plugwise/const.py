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

# binary_sensor const:
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

# sensor consts:
ATTR_TEMPERATURE = ["Temperature", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE]
ATTR_BATTERY_LEVEL = ["Charge", PERCENTAGE, DEVICE_CLASS_BATTERY]
ATTR_ILLUMINANCE = ["Illuminance", UNIT_LUMEN, DEVICE_CLASS_ILLUMINANCE]
ATTR_PRESSURE = ["Pressure", PRESSURE_BAR, DEVICE_CLASS_PRESSURE]
TEMP_SENSOR_MAP = {
    "setpoint": ATTR_TEMPERATURE,
    "temperature": ATTR_TEMPERATURE,
    "intended_boiler_temperature": ATTR_TEMPERATURE,
    "temperature_difference": ATTR_TEMPERATURE,
    "outdoor_temperature": ATTR_TEMPERATURE,
    "water_temperature": ATTR_TEMPERATURE,
    "return_temperature": ATTR_TEMPERATURE,
}
ENERGY_SENSOR_MAP = {
    "electricity_consumed": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER],
    ],
    "electricity_produced": [
        "Current Produced Power",
        POWER_WATT,
        DEVICE_CLASS_POWER],
    ],
    "electricity_consumed_interval": [
        "Consumed Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_peak_interval": [
        "Consumed Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_off_peak_interval": [
        "Consumed Power Interval (off peak)",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_interval": [
        "Produced Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_peak_interval": [
        "Produced Power Interval",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_off_peak_interval": [
        "Produced Power Interval (off peak)",
        ENERGY_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_off_peak_point": [
        "Current Consumed Power (off peak)",
        POWER_WATT,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_peak_point": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_consumed_peak_cumulative": [
        "Cumulative Consumed Power",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_off_peak_point": [
        "Current Consumed Power (off peak)",
        POWER_WATT,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_peak_point": [
        "Current Consumed Power",
        POWER_WATT,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_off_peak_cumulative": [
        "Cumulative Consumed Power (off peak)",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "electricity_produced_peak_cumulative": [
        "Cumulative Consumed Power",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
    "gas_consumed_interval": [
        "Current Consumed Gas",
        VOLUME_CUBIC_METERS,
        None,
    ],
    "gas_consumed_cumulative": [
        "Cumulative Consumed Gas",
        VOLUME_CUBIC_METERS,
        None,
    ],
    "net_electricity_point": [
        "Current net Power",
        POWER_WATT,
        DEVICE_CLASS_POWER
    ],
    "net_electricity_cumulative": [
        "Cumulative net Power",
        ENERGY_KILO_WATT_HOUR,
        DEVICE_CLASS_POWER,
    ],
}
MISC_SENSOR_MAP = {
    "battery": ATTR_BATTERY_LEVEL,
    "illuminance": ATTR_ILLUMINANCE,
    "modulation_level": ["Heater Modulation Level", PERCENTAGE, None],
    "valve_position": ["Valve Position", PERCENTAGE, None],
    "water_pressure": ATTR_PRESSURE,
}
INDICATE_ACTIVE_LOCAL_DEVICE = [
    "cooling_state",
    "flame_state",
]
CUSTOM_ICONS = {
    "gas_consumed_interval": "mdi:fire",
    "gas_consumed_cumulative": "mdi:fire",
    "modulation_level": "mdi:percent",
    "valve_position": "mdi:valve",
}

# switch const:
SWITCH_CLASSES = ["plug", "switch_group"]