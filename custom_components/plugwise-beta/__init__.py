"""Plugwise platform for Home Assistant Core."""

import asyncio
import logging
from datetime import timedelta
from typing import Optional
import voluptuous as vol

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant 
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from Plugwise_Smile.Smile import Smile

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

SENSOR_PLATFORMS = ["sensor"]
ALL_PLATFORMS = ["binary_sensor", "climate", "sensor", "switch"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Plugwise platform."""
    return True


async def async_setup_entry(hass, entry):
    """Set up Plugwise Smiles from a config entry."""
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(
        host=entry.data["host"], password=entry.data["password"], websession=websession
    )

    try:
        connected = await api.connect()

        if not connected:
            _LOGGER.error("Unable to connect to Smile: %s",api.smile_status)
            raise ConfigEntryNotReady

    except Smile.InvalidAuthentication:
        _LOGGER.error("Invalid Smile ID")
        return False

    except Smile.PlugwiseError:
        _LOGGER.error("Error while communicating to device")
        raise ConfigEntryNotReady

    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while connecting to Smile")
        raise ConfigEntryNotReady

    if api.smile_type == "power":
        update_interval = timedelta(seconds=10)
    else:
        update_interval = timedelta(seconds=60)

    async def async_update_data():
        """Update data via API endpoint."""
        _LOGGER.debug("Updating Smile %s", api.smile_type)
        try:
            async with async_timeout.timeout(10):
                await api.full_update_device()
                _LOGGER.debug("Succesfully updated Smile %s", api.smile_type)
                return True
        except Smile.XMLDataMissingError:
            _LOGGER.debug("Updating Smile failed %s", api.smile_type)
            raise UpdateFailed("Smile update failed %s", api.smile_type)


    api.get_all_devices()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Smile",
        update_method=async_update_data,
        update_interval=update_interval)

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    _LOGGER.debug("Async update interval %s", update_interval)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = { "api": api, "coordinator": coordinator }

    _LOGGER.debug("Gateway is %s", api.gateway_id)

    _LOGGER.debug("Gateway sofware version is %s", api.smile_version)
    _LOGGER.debug("Appliances is %s", api.get_all_appliances())
    _LOGGER.debug("Scan thermostats is %s", api.scan_thermostats())
    _LOGGER.debug("Locations (matched) is %s", api.match_locations())

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, api.gateway_id)},
        manufacturer="Plugwise",
        name=entry.title,
        model=f"Smile {api.smile_name}",
        sw_version=api.smile_version[0],
    )

    single_master_thermostat = api.single_master_thermostat()
    _LOGGER.debug("Single master thermostat = %s", single_master_thermostat)
    platforms = ALL_PLATFORMS
    if single_master_thermostat is None:
        platforms = SENSOR_PLATFORMS

    for component in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in ALL_PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class SmileGateway(Entity):
    """Represent Smile Gateway."""

    def __init__(self, api, coordinator):
        """Initialise the sensor."""
        self._api = api
        self._coordinator = coordinator
        self._unique_id = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def should_poll(self):
        """Return False, updates are controlled via coordinator."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self._process_data)
        )
    
    def _process_data(self):
        """Interpret and process API data."""
        raise NotImplementedError

    async def async_update(self):
        """Update the entity."""
        await self._coordinator.async_request_refresh()
