"""Constants for Plugwise component."""
from datetime import timedelta
import logging
from typing import Final

import voluptuous as vol  # pw-beta usb

from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

DOMAIN: Final = "plugwise"

LOGGER = logging.getLogger(__package__)

API: Final = "api"
COORDINATOR: Final = "coordinator"
CONF_HOMEKIT_EMULATION: Final = "homekit_emulation"  # pw-beta options
CONF_REFRESH_INTERVAL: Final = "refresh_interval"  # pw-beta options
CONF_MANUAL_PATH: Final = "Enter Manually"
GATEWAY: Final = "gateway"
PW_TYPE: Final = "plugwise_type"
SMILE: Final = "smile"
STICK: Final = "stick"
STRETCH: Final = "stretch"
STRETCH_USERNAME: Final = "stretch"
USB: Final = "usb"

FLOW_NET: Final = "Network: Smile/Stretch"
FLOW_SMILE: Final = "Smile (Adam/Anna/P1)"
FLOW_STRETCH: Final = "Stretch (Stretch)"
FLOW_TYPE: Final = "flow_type"
FLOW_USB: Final = "USB: Stick"

UNDO_UPDATE_LISTENER: Final = "undo_update_listener"

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
PLATFORMS_GATEWAY: Final[list[str]] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]
SENSOR_PLATFORMS: Final[list[str]] = [Platform.SENSOR, Platform.SWITCH]
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

# --- Const for Plugwise USB-stick.

PLATFORMS_USB: Final[list[str]] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]
CONF_USB_PATH: Final = "usb_path"

# Callback types
CB_NEW_NODE: Final = "NEW_NODE"
CB_JOIN_REQUEST: Final = "JOIN_REQUEST"


# USB generic device constants
USB_AVAILABLE_ID: Final = "available"

ATTR_MAC_ADDRESS: Final = "mac"

SERVICE_USB_DEVICE_ADD: Final = "device_add"
SERVICE_USB_DEVICE_REMOVE: Final = "device_remove"
SERVICE_USB_DEVICE_SCHEMA: Final = vol.Schema(
    {vol.Required(ATTR_MAC_ADDRESS): cv.string}
)  # pw-beta usb


# USB Relay device constants
USB_RELAY_ID: Final = "relay"


# USB SED (battery powered) device constants
ATTR_SED_STAY_ACTIVE: Final = "stay_active"
ATTR_SED_SLEEP_FOR: Final = "sleep_for"
ATTR_SED_MAINTENANCE_INTERVAL: Final = "maintenance_interval"
ATTR_SED_CLOCK_SYNC: Final = "clock_sync"
ATTR_SED_CLOCK_INTERVAL: Final = "clock_interval"

SERVICE_USB_SED_BATTERY_CONFIG: Final = "configure_battery_savings"
SERVICE_USB_SED_BATTERY_CONFIG_SCHEMA: Final = {
    vol.Required(ATTR_SED_STAY_ACTIVE): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=120)
    ),
    vol.Required(ATTR_SED_SLEEP_FOR): vol.All(
        vol.Coerce(int), vol.Range(min=10, max=60)
    ),
    vol.Required(ATTR_SED_MAINTENANCE_INTERVAL): vol.All(
        vol.Coerce(int), vol.Range(min=5, max=1440)
    ),
    vol.Required(ATTR_SED_CLOCK_SYNC): cv.boolean,
    vol.Required(ATTR_SED_CLOCK_INTERVAL): vol.All(
        vol.Coerce(int), vol.Range(min=60, max=10080)
    ),
}


# USB Scan device constants
USB_MOTION_ID: Final = "motion"

ATTR_SCAN_DAYLIGHT_MODE: Final = "day_light"
ATTR_SCAN_SENSITIVITY_MODE: Final = "sensitivity_mode"
ATTR_SCAN_RESET_TIMER: Final = "reset_timer"

SCAN_SENSITIVITY_HIGH: Final = "high"
SCAN_SENSITIVITY_MEDIUM: Final = "medium"
SCAN_SENSITIVITY_OFF: Final = "off"
SCAN_SENSITIVITY_MODES = [
    SCAN_SENSITIVITY_HIGH,
    SCAN_SENSITIVITY_MEDIUM,
    SCAN_SENSITIVITY_OFF,
]

SERVICE_USB_SCAN_CONFIG: Final = "configure_scan"
SERVICE_USB_SCAN_CONFIG_SCHEMA = (
    {
        vol.Required(ATTR_SCAN_SENSITIVITY_MODE): vol.In(SCAN_SENSITIVITY_MODES),
        vol.Required(ATTR_SCAN_RESET_TIMER): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=240)
        ),
        vol.Required(ATTR_SCAN_DAYLIGHT_MODE): cv.boolean,
    },
)
