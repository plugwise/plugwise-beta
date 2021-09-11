"""Constants for Plugwise beta component."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import DEVICE_CLASS_MOTION
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntityDescription,
)
from homeassistant.components.switch import DEVICE_CLASS_OUTLET
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TIME_MILLISECONDS,
)
from homeassistant.helpers.entity import EntityDescription

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
USB_MOTION_ID = "motion"
USB_RELAY_ID = "relay"


@dataclass
class PlugwiseUSBRequiredKeysMixin:
    """Mixin for required keys."""

    state_request_method: str


@dataclass
class PlugwiseUSBEntityDescription(EntityDescription, PlugwiseUSBRequiredKeysMixin):
    """Generic Plugwise USB entity description."""


@dataclass
class PlugwiseUSBSensorEntityDescription(
    SensorEntityDescription, PlugwiseUSBEntityDescription
):
    """Describes Plugwise USB sensor entity."""


@dataclass
class PlugwiseUSBSwitchEntityDescription(
    SwitchEntityDescription, PlugwiseUSBEntityDescription
):
    """Describes Plugwise USB switch entity."""


@dataclass
class PlugwiseUSBBinarySensorEntityDescription(
    BinarySensorEntityDescription, PlugwiseUSBEntityDescription
):
    """Describes Plugwise USB binary sensor entity."""


USB_SENSOR_TYPES: tuple[PlugwiseUSBSensorEntityDescription, ...] = (
    PlugwiseUSBSensorEntityDescription(
        key="ping",
        name="Ping roundtrip",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TIME_MILLISECONDS,
        state_request_method="ping",
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_1s",
        device_class=DEVICE_CLASS_POWER,
        name="Power usage",
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
        state_request_method="current_power_usage",
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_8s",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power usage 8 seconds",
        state_request_method="current_power_usage_8_sec",
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_con_cur_hour",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power consumption current hour",
        state_request_method="power_consumption_current_hour",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_con_prev_hour",
        device_class=DEVICE_CLASS_POWER,
        name="Power consumption previous hour",
        state_request_method="power_consumption_previous_hour",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="energy_consumption_today",
        device_class=DEVICE_CLASS_ENERGY,
        name="Energy consumption today",
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_request_method="energy_consumption_today",
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_con_today",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power consumption today",
        state_request_method="power_consumption_today",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_con_yesterday",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power consumption yesterday",
        state_request_method="power_consumption_yesterday",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_prod_cur_hour",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power production current hour",
        state_request_method="power_production_current_hour",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="power_prod_prev_hour",
        device_class=DEVICE_CLASS_POWER,
        entity_registry_enabled_default=False,
        name="Power production previous hour",
        state_request_method="power_production_previous_hour",
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="RSSI_in",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        name="Inbound RSSI",
        state_request_method="rssi_in",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    ),
    PlugwiseUSBSensorEntityDescription(
        key="RSSI_out",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        name="Outbound RSSI",
        state_request_method="rssi_out",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    ),
)


USB_SWITCH_TYPES: tuple[PlugwiseUSBSwitchEntityDescription, ...] = (
    PlugwiseUSBSwitchEntityDescription(
        key=USB_RELAY_ID,
        device_class=DEVICE_CLASS_OUTLET,
        name="Relay state",
        state_request_method="relay_state",
    ),
)


USB_BINARY_SENSOR_TYPES: tuple[PlugwiseUSBBinarySensorEntityDescription, ...] = (
    PlugwiseUSBBinarySensorEntityDescription(
        key=USB_MOTION_ID,
        device_class=DEVICE_CLASS_MOTION,
        name="Motion",
        state_request_method="motion",
    ),
)


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
