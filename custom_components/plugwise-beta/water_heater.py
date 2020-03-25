#!/usr/bin/env python3
import logging
import voluptuous as vol
from functools import partial

from Plugwise_Smile.Smile import Smile

from datetime import timedelta
import async_timeout
from typing import Any, Dict

from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import callback

from homeassistant.helpers.entity import Entity

from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    TEMP_CELSIUS,
)

from .const import (
    CONF_THERMOSTAT,
    CURRENT_HVAC_DHW,
    DOMAIN,
    WATER_HEATER_ICON,
)

import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

# Scan interval for updating sensor values
# Smile communication is set using configuration directives
SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Smile sensors from a config entry."""
    api = hass.data[DOMAIN][config_entry.entry_id]['api']
    updater = hass.data[DOMAIN][config_entry.entry_id]['updater']

#    # Stay close to meter measurements for power, for thermostat back off a bit
#    if api._smile_type == 'power':
#        update_interval=timedelta(seconds=10)
#    else:
#        update_interval=timedelta(seconds=60)
#
#    wh_coordinator = DataUpdateCoordinator(
#        hass,
#        _LOGGER,
#        name="water_heater",
#        update_method=partial(async_safe_fetch,api),
#        update_interval=update_interval
#    )
#
#    # First do a refresh to see if we can reach the hub.
#    # Otherwise we will declare not ready.
#    await wh_coordinator.async_refresh()
#
#    if not wh_coordinator.last_update_success:
#        raise PlatformNotReady

    devices = []
    all_devices=api.get_all_devices()
    for dev_id,device in all_devices.items():
        if device['class'] != 'heater_central':
            continue
        data = api.get_device_data(dev_id)

        _LOGGER.info('Plugwise sensor Dev %s', device['name'])
        water_heater = PwWaterHeater(api, updater, device['name'], dev_id)

        if not water_heater:
            continue

        devices.append(water_heater)

    async_add_entities(devices, True)

#async def async_safe_fetch(api):
#    """Safely fetch data."""
#    with async_timeout.timeout(10):
#        await api.full_update_device()
#        return await api.get_devices()
#
class PwWaterHeater(Entity):
    """Representation of a Plugwise water_heater."""

    # def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id):
    def __init__(self, api, updater, name, dev_id):
        """Set up the Plugwise API."""
        self._api = api
        self._updater = updater
        self._name = name
        self._dev_id = dev_id
        self._heating_status =  None
        self._boiler_status = None
        self._dhw_status = None
        self._unique_id = f"{dev_id}-water_heater"

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
    def state(self):
        """Return the state of the sensor."""
        if self._heating_status or self._boiler_status:
            return CURRENT_HVAC_HEAT
        if self._dhw_status:
            return CURRENT_HVAC_DHW
        return CURRENT_HVAC_IDLE

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return WATER_HEATER_ICON

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    def update(self):
        """Update the entity."""

        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
        else:
            if 'central_heating_state' in data:
                self._heating_status =  data['central_heating_state']
            if 'boiler_state' in data:
                self._boiler_status = data['boiler_state']
            if 'dhw_state' in data:
                self._dhw_status = data['dhw_state']

