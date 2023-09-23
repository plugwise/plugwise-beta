"""Constants for Plugwise component."""
from datetime import timedelta
import logging
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "plugwise"

LOGGER = logging.getLogger(__package__)

API: Final = "api"
COORDINATOR: Final = "coordinator"
CONF_HOMEKIT_EMULATION: Final = "homekit_emulation"  # pw-beta options
CONF_REFRESH_INTERVAL: Final = "refresh_interval"  # pw-beta options
CONF_MANUAL_PATH: Final = "Enter Manually"
SMILE: Final = "smile"
STRETCH: Final = "stretch"
STRETCH_USERNAME: Final = "stretch"
UNIQUE_IDS: Final = "unique_ids"

FLOW_NET: Final = "Network: Smile/Stretch"
FLOW_SMILE: Final = "Smile (Adam/Anna/P1)"
FLOW_STRETCH: Final = "Stretch (Stretch)"
FLOW_TYPE: Final = "flow_type"

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
