"""Plugwise Smile Helper Classes."""
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
)

from .const import (
    COOLING_ICON,
    FLAME_ICON,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    HEATING_ICON,
    IDLE_ICON,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
    SEVERITIES,
)


def icon_selector(arg, state):
    """Icon-selection helper function."""
    selector = {
        # Device State icons
        "cooling": COOLING_ICON,
        "dhw-heating": FLAME_ICON,
        "dhw and cooling": COOLING_ICON,
        "dhw and heating": HEATING_ICON,
        "heating": HEATING_ICON,
        "idle": IDLE_ICON,
        # Binary Sensor icons
        "dhw_state": FLOW_ON_ICON if state else FLOW_OFF_ICON,
        "flame_state": FLAME_ICON if state else IDLE_ICON,
        "slave_boiler_state": FLAME_ICON if state else IDLE_ICON,
        "plugwise_notification": NOTIFICATION_ICON if state else NO_NOTIFICATION_ICON,
    }
    return selector.get(arg)


class GWBinarySensor:
    """Represent the Plugwise Smile/Stretch binary_sensor."""

    def __init__(self, data, dev_id, binary_sensor):
        """Initialize the Gateway."""
        self._attributes = {}
        self._binary_sensor = binary_sensor
        self._data = data
        self._dev_id = dev_id
        self._notification = {}

    @property
    def extra_state_attributes(self):
        """Gateway binary_sensor extra state attributes."""
        notify = self._data[0]["notifications"]
        self._notification = {}
        for severity in SEVERITIES:
            self._attributes[f"{severity.upper()}_msg"] = []
        if notify != {}:
            for notify_id, details in notify.items():
                for msg_type, msg in details.items():
                    if msg_type not in SEVERITIES:
                        msg_type = "other"  # pragma: no cover

                    self._attributes[f"{msg_type.upper()}_msg"].append(msg)
                    self._notification[notify_id] = f"{msg_type.title()}: {msg}"

        return None if not self._attributes else self._attributes

    @property
    def is_on(self):
        """Gateway binary_sensor state."""
        return self._data[1][self._dev_id]["binary_sensors"][self._binary_sensor]

    @property
    def icon(self):
        """Gateway binary_sensor icon."""
        return icon_selector(self._binary_sensor, self.is_on)

    @property
    def notification(self):
        """Plugwise Notification message."""
        return self._notification


class GWThermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, data, dev_id):
        """Initialize the Thermostat."""

        self._data = data
        self._dev_id = dev_id
        self._heater_id = self._data[0]["heater_id"]

    @property
    def cooling_active(self):
        """Cooling state."""
        return self._data[1][self._heater_id]["cooling_active"]

    @property
    def cooling_state(self):
        """Cooling state."""
        cooling_state = self._data[1][self._heater_id]["cooling_state"]
        # When control_state is present, prefer this data
        if "control_state" in self._data[1][self._dev_id]:
            cooling_state = self._data[1][self._dev_id]["control_state"] == "cooling"
        
        return cooling_state

    @property
    def heating_state(self):
        """Heating state."""
        heating_state = self._data[1][self._heater_id]["heating_state"]
        # When control_state is present, prefer this data
        if "control_state" in self._data[1][self._dev_id]:
            heating_state = self._data[1][self._dev_id]["control_state"] == "heating"

        return heating_state

    @property
    def preset_modes(self):
        """Climate preset modes."""
        get_presets = self._data[1][self._dev_id]["presets"]
        if get_presets:
            preset_modes = list(get_presets)
            return preset_modes

        return None

