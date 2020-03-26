"""Plugwise components for Home Assistant Core."""
import asyncio
import logging

import voluptuous as vol
from datetime import timedelta
from typing import Optional

from Plugwise_Smile.Smile import Smile

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers import device_registry as dr

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

# HVAC modes
HVAC_MODES_1 = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
HVAC_MODES_2 = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO]

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE)

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = ["sensor","climate", "water_heater"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Plugwise platform."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plugwise Smiles from a config entry."""
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(host=entry.data.get("host"),
                password=entry.data.get("password"),
                websession=websession)

    await api.connect()

    if api._smile_type == 'power':
        update_interval=timedelta(seconds=10)
    else:
        update_interval=timedelta(seconds=60)

    _LOGGER.debug("Plugwise async update interval %s",update_interval)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "updater": SmileDataUpdater(
            hass, "device", entry.entry_id, api, "full_update_device", update_interval
        ),
    }

    _LOGGER.debug("Plugwise gateway is %s",api._gateway_id)
    device_registry = await dr.async_get_registry(hass)
    _LOGGER.debug("Plugwise device registry  %s",device_registry)
    result = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, api._gateway_id)},
        manufacturer="Plugwise",
        name="{} - {} Gateway".format(entry.title, api._smile_name),
        model=api._smile_name,
        sw_version=api._smile_version[0],
    )
    _LOGGER.debug("Plugwise device registry  %s",result)
    #connections={(dr.CONNECTION_NETWORK_MAC, config.mac)},
    #model=config.modelid,
    #sw_version=config.swversion,

    #_LOGGER.debug("Plugwise async entry hass data %s",hass.data[DOMAIN])
    # hass.data[DOMAIN][entry.entry_id] = api

    for component in PLATFORMS: #api._platforms
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async def async_refresh_all(_):
        """Refresh all Smile data."""
        for info in hass.data[DOMAIN].values():
            await info["updater"].async_refresh_all()

    # Register service
    hass.services.async_register(DOMAIN, "update", async_refresh_all)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class SmileDataUpdater:
    """Data storage for single API endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        data_type: str,
        config_entry_id: str,
        api: Smile,
        update_method: str,
        update_interval: timedelta,
    ):
        """Initialize global data updater."""
        self.hass = hass
        self.data_type = data_type
        self.config_entry_id = config_entry_id
        self.api = api
        self.update_method = update_method
        self.update_interval = update_interval
        self.listeners = []
        self._unsub_interval = None

    @callback
    def async_add_listener(self, update_callback):
        """Listen for data updates."""
        # This is the first listener, set up interval.
        if not self.listeners:
            self._unsub_interval = async_track_time_interval(
                self.hass, self.async_refresh_all, self.update_interval
            )

        self.listeners.append(update_callback)

    @callback
    def async_remove_listener(self, update_callback):
        """Remove data update."""
        self.listeners.remove(update_callback)

        if not self.listeners:
            self._unsub_interval()
            self._unsub_interval = None

    async def async_refresh_all(self, _now: Optional[int] = None) -> None:
        """Time to update."""
        _LOGGER.debug("Plugwise Smile updating with interval: %s", self.update_interval)
        if not self.listeners:
            _LOGGER.debug("Plugwise Smile has no listeners, not updating")
            return

        _LOGGER.debug("Plugwise Smile updating data using: %s", self.update_method)
        #await self.hass.async_add_executor_job(
            # getattr(self.api, self.update_method)
        #)
        await self.api.full_update_device()

        for update_callback in self.listeners:
            update_callback()

