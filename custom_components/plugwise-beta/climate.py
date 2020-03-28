#!/usr/bin/env python3
import logging
from datetime import timedelta
from typing import Dict

from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (CURRENT_HVAC_COOL,
                                                    CURRENT_HVAC_HEAT,
                                                    CURRENT_HVAC_IDLE,
                                                    HVAC_MODE_AUTO,
                                                    HVAC_MODE_HEAT,
                                                    HVAC_MODE_HEAT_COOL,
                                                    HVAC_MODE_OFF,
                                                    SUPPORT_PRESET_MODE,
                                                    SUPPORT_TARGET_TEMPERATURE)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback

from . import HVAC_MODES_1, HVAC_MODES_2
from .const import DOMAIN, THERMOSTAT_ICON

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

_LOGGER = logging.getLogger(__name__)

# Scan interval for updating climate values
# Smile communication is set using configuration directives
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile Thermostats from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    updater = hass.data[DOMAIN][config_entry.entry_id]["updater"]

    #    if api._smile_type == 'power':
    #        update_interval=timedelta(seconds=10)
    #    else:
    #        update_interval=timedelta(seconds=60)
    #
    #    climate_coordinator = DataUpdateCoordinator(
    #        hass,
    #        _LOGGER,
    #        name="climate",
    #        update_method=partial(async_safe_fetch,api),
    #        update_interval=update_interval
    #    )
    #
    #    # First do a refresh to see if we can reach the hub.
    #    # Otherwise we will declare not ready.
    #    await climate_coordinator.async_refresh()
    #
    #    if not climate_coordinator.last_update_success:
    #        raise PlatformNotReady

    devices = []
    all_devices = api.get_all_devices()
    for dev_id, device in all_devices.items():

        if device["class"] != "thermostat" and device["class"] != "zone_thermostat":
            continue
        # data = api.get_device_data(dev_id)

        _LOGGER.info("Plugwise climate Dev %s", device["name"])
        thermostat = PwThermostat(
            api, updater, device["name"], dev_id, device["location"], 4, 30
        )

        if not thermostat:
            continue

        devices.append(thermostat)
        _LOGGER.info("Added climate.%s", "{}".format(device["name"]))

    async_add_entities(devices, True)


# async def async_safe_fetch(api):
#    """Safely fetch data."""
#    with async_timeout.timeout(10):
#        await api.full_update_device()
#        return await api.get_devices()


class PwThermostat(ClimateDevice):
    """Representation of an Plugwise thermostat."""

    # def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id, min_temp, max_temp):
    def __init__(self, api, updater, name, dev_id, loc_id, min_temp, max_temp):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._loc_id = loc_id
        self._min_temp = min_temp
        self._max_temp = max_temp

        self._selected_schema = None
        self._last_active_schema = None
        self._preset_mode = None
        self._presets = None
        self._presets_list = None
        self._boiler_status = None
        self._cooling_status = None
        self._domestic_hot_water_state = None
        self._central_heating_state = None
        self._schema_names = None
        self._schema_status = None
        self._temperature = None
        self._thermostat = None
        self._boiler_temp = None
        self._water_pressure = None
        self._schedule_temp = None
        self._hvac_mode = None
        self._unique_id = f"{dev_id}-climate"

        cdata = api.get_device_data(self._api._gateway_id)
        if "central_heating_state" in cdata:
            self._central_heating_state = cdata["central_heating_state"] == "on"
        if "domestic_hot_water_state" in cdata:
            self._domestic_hot_water_state = cdata["domestic_hot_water_state"] == "on"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._updater.async_add_listener(self._update_callback)

    async def async_will_remove_from_hass(self):
        """Disconnect callbacks."""
        self._updater.async_remove_listener(self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.update()
        self.async_write_ha_state()

    @property
    def hvac_action(self):
        """Return the current action."""
        if (
            self._central_heating_state
            or self._boiler_status
            or self._domestic_hot_water_state
        ):
            return CURRENT_HVAC_HEAT
        if self._cooling_status:
            return CURRENT_HVAC_COOL
        return CURRENT_HVAC_IDLE

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": "Plugwise",
            "via_device": (DOMAIN, self._api._gateway_id),
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return THERMOSTAT_ICON

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attributes = {}
        if self._schema_names:
            attributes["available_schemas"] = self._schema_names
        if self._selected_schema:
            attributes["selected_schema"] = self._selected_schema
        return attributes

    @property
    def preset_modes(self):
        """
        Return the available preset modes list and make the presets with their
        temperatures available.
        """
        return self._presets_list

    @property
    def hvac_modes(self):
        """Return the available hvac modes list."""
        if self._central_heating_state is not None or self._boiler_status is not None:
            if self._cooling_status is not None:
                return HVAC_MODES_2
            return HVAC_MODES_1

    @property
    def hvac_mode(self):
        """Return current active hvac state."""
        if self._schema_status:
            return HVAC_MODE_AUTO
        if (
            self._central_heating_state
            or self._boiler_status
            or self._domestic_hot_water_state
        ):
            if self._cooling_status:
                return HVAC_MODE_HEAT_COOL
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def target_temperature(self):
        """Return the target_temperature.
        From the XML the thermostat-value is used because it updates 'immediately'
        compared to the target_temperature-value. This way the information on the card
        is "immediately" updated after changing the preset, temperature, etc.
        """
        return self._thermostat

    @property
    def preset_mode(self):
        """Return the active preset."""
        if self._presets:
            return self._preset_mode
        return None

    @property
    def current_temperature(self):
        """Return the current room temperature."""
        return self._temperature

    @property
    def min_temp(self):
        """Return the minimal temperature possible to set."""
        return self._min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature possible to set."""
        return self._max_temp

    @property
    def temperature_unit(self):
        """Return the unit of measured temperature."""
        return TEMP_CELSIUS

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if (temperature is not None) and (
            self._min_temp < temperature < self._max_temp
        ):
            _LOGGER.debug("Set temp to %sºC", temperature)
            await self._api.set_temperature(self._loc_id, temperature)
            await self._updater.async_refresh_all()
        else:
            _LOGGER.error("Invalid temperature requested")

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the hvac mode."""
        _LOGGER.debug("Set hvac_mode to: %s", hvac_mode)
        state = "false"
        if hvac_mode == HVAC_MODE_AUTO:
            state = "true"
        await self._api.set_schedule_state(
            self._loc_id, self._last_active_schema, state
        )
        await self._updater.async_refresh_all()

    async def async_set_preset_mode(self, preset_mode):
        _LOGGER.debug("Set preset mode to %s.", preset_mode)
        """Set the preset mode."""
        await self._api.set_preset(self._loc_id, preset_mode)
        await self._updater.async_refresh_all()

    def update(self):
        """Update the data for this climate device."""
        _LOGGER.info("Updating climate...")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            _LOGGER.debug("Device data collected from Plugwise API")
            if "thermostat" in data:
                self._thermostat = data["thermostat"]
            if "temperature" in data:
                self._temperature = data["temperature"]
            if "boiler_temp" in data:
                self._boiler_temp = data["boiler_temp"]
            if "available_schedules" in data:
                self._schema_names = data["available_schedules"]
            if "selected_schedule" in data:
                self._selected_schema = data["selected_schedule"]
                if self._selected_schema is not None:
                    self._schema_status = True
                    self._schedule_temp = self._thermostat
                else:
                    self._schema_status = False
            if "last_used" in data:
                self._last_active_schema = data["last_used"]
            if "presets" in data:
                self._presets = data["presets"]
                if self._presets:
                    self._presets_list = list(self._presets)
            if "active_preset" in data:
                self._preset_mode = data["active_preset"]
            if "boiler_state" in data:
                self._boiler_status = data["boiler_state"] == "on"
            if "central_heating_state" in data:
                self._central_heating_state = data["central_heating_state"] == "on"
            if "cooling_state" in data:
                self._cooling_status = data["cooling_state"] == "on"
            if "domestic_hot_water_state" in data:
                self._domestic_hot_water_state = (
                    data["domestic_hot_water_state"] == "on"
                )
