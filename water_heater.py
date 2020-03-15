#!/usr/bin/env python3
import logging
import voluptuous as vol
from functools import partial

from Plugwise_Smile.Smile import Smile

from datetime import timedelta
import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    api = hass.data[DOMAIN][config_entry.unique_id]

    # Stay close to meter measurements for power, for thermostat back off a bit
    if api._smile_type == 'power':
        update_interval=timedelta(seconds=10)
    else:
        update_interval=timedelta(seconds=60)

    wh_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="water_heater",
        update_method=partial(async_safe_fetch,api),
        update_interval=update_interval
    )

    # First do a refresh to see if we can reach the hub.
    # Otherwise we will declare not ready.
    await wh_coordinator.async_refresh()

    if not wh_coordinator.last_update_success:
        raise PlatformNotReady

    devices = []
    ctrl_id = None
    data = None
    idx = 0
    if api._smile_type == 'thermostat':
      for dev in wh_coordinator.data:
          _LOGGER.info('Dev %s', dev)
          if dev['name'] == 'Controlled Device':
              ctrl_id = dev['id']
              dev_id = None
              name = dev['name']
              _LOGGER.info('Name %s', name)
              data = api.get_device_data(dev_id, ctrl_id)

              if data is None:
                  _LOGGER.debug("Received no data for device %s.", name)
                  return

              device = PwWaterHeater(wh_coordinator, idx, api, dev['name'], dev_id, ctrl_id)
              if not device:
                  continue
              idx += 1
              devices.append(device)
    async_add_entities(devices, True)

async def async_safe_fetch(api):
    """Safely fetch data."""
    with async_timeout.timeout(10):
        await api.full_update_device()
        return await api.get_devices()

class PwWaterHeater(Entity):
    """Representation of a Plugwise water_heater."""

    def __init__(self, coordinator, idx, api, name, dev_id, ctlr_id):
        """Set up the Plugwise API."""
        self.coordinator = coordinator
        self.idx = idx
        self._api = api
        self._name = name
        self._dev_id = dev_id
        self._ctrl_id = ctlr_id
        self._heating_status =  None
        self._boiler_status = None
        self._dhw_status = None

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self._name

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
    def is_on(self):
      """Return entity state.

      Example to show how we fetch data from coordinator.
      """
      self.coordinator.data[self.idx]['state']

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(
            self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(
            self.async_write_ha_state
        )

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()

        _LOGGER.debug("Update sensor called")
        data = self._api.get_device_data(self._dev_id, self._ctrl_id)

        if data is None:
            _LOGGER.debug("Received no data for device %s.", self._name)
            return
        if 'central_heating_state' in data:
            self._heating_status =  data['central_heating_state']
        if 'boiler_state' in data:
            self._boiler_status = data['boiler_state']
        if 'dhw_state' in data:
            self._dhw_status = data['dhw_state']

