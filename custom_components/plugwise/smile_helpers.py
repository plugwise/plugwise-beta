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

        self._cooling_active = False
        self._cooling_state = False
        self._data = data
        self._dev_id = dev_id
        self._extra_state_attributes = None
        self._get_presets = None
        self._heating_state = False
        self._hvac_mode = HVAC_MODE_AUTO
        self._last_active_schema = None
        self._preset_mode = None
        self._preset_modes = None
        self._schedule_temp = None
        self._schedules = []
        self._schedule_status = False
        self._selected_schedule = None
        self._setpoint = None
        self._temperature = None

        self._active_device_present = self._data[0]["active_device"]
        self._cooling_present = self._data[0]["cooling_present"]
        self._heater_id = self._data[0]["heater_id"]

    @property
    def cooling_present(self):
        """Cooling function presence."""
        self._cooling_present = self._data[0]["cooling_present"]
        return self._cooling_present

    @property
    def cooling_state(self):
        """Cooling state."""
        if self._active_device_present:
            return self._data[1][self._heater_id]["cooling_state"]
        # When control_state is present, prefer this data
        if "control_state" in self._data[1][self._dev_id]:
            return self._data[1][self._dev_id]["control_state"] == "cooling"

    @property
    def heating_state(self):
        """Heating state."""
        if self._active_device_present:
            return self._data[1][self._heater_id]["heating_state"]
        # When control_state is present, prefer this data
        if "control_state" in self._data[1][self._dev_id]:
            return self._data[1][self._dev_id]["control_state"] == "heating"

    @property
    def hvac_mode(self):
        """Climate active HVAC mode."""
        self._hvac_mode = HVAC_MODE_AUTO
        if "selected_schedule" in self._data[1][self._dev_id]:
            self._selected_schedule = self._data[1][self._dev_id]["selected_schedule"]
            self._schedule_status = False
            if self._selected_schedule is not None:
                self._schedule_status = True

        if not self._schedule_status:
            if self._preset_mode == PRESET_AWAY:
                self._hvac_mode = HVAC_MODE_OFF  # pragma: no cover
            else:
                self._hvac_mode = HVAC_MODE_HEAT
                if self._cooling_present:
                    self._hvac_mode = HVAC_MODE_COOL

        return self._hvac_mode

    @property
    def presets(self):
        """Climate list of presets."""
        return self._data[1][self._dev_id]["presets"]

    @property
    def preset_mode(self):
        """Climate active preset mode."""
        self._preset_mode = self._data[1][self._dev_id]["active_preset"]
        return self._preset_mode

    @property
    def preset_modes(self):
        """Climate preset modes."""
        self._get_presets = self._data[1][self._dev_id]["presets"]
        if self._get_presets:
            self._preset_modes = list(self._get_presets)
        return self._preset_modes

    @property
    def last_active_schema(self):
        """Climate last active schema."""
        return self._data[1][self._dev_id]["last_used"]

    @property
    def current_temperature(self):
        """Climate current measured temperature."""
        return self._data[1][self._dev_id]["sensors"]["temperature"]

    @property
    def target_temperature(self):
        """Climate target temperature."""
        return self._data[1][self._dev_id]["sensors"]["setpoint"]

    @property
    def schedule_temperature(self):
        """Climate target temperature."""
        return self._data[1][self._dev_id]["schedule_temperature"]

    @property
    def extra_state_attributes(self):
        """Climate extra state attributes."""
        attributes = {}
        self._schedules = self._data[1][self._dev_id].get("available_schedules")
        self._selected_schedule = self._data[1][self._dev_id].get("selected_schedule")
        if self._schedules:
            attributes["available_schemas"] = self._schedules
        if self._selected_schedule:
            attributes["selected_schema"] = self._selected_schedule

        return attributes
