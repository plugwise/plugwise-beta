"""Plugwise platform for Home Assistant Core."""

import asyncio
import logging
from datetime import timedelta
from typing import Dict

import async_timeout
import voluptuous as vol
from Plugwise_Smile.Smile import Smile

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from .const import COORDINATOR, DEFAULT_SCAN_INTERVAL, DOMAIN, UNDO_UPDATE_LISTENER

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

SERVICE_DELETE = "delete_notification"

SENSOR_PLATFORMS = ["sensor", "switch"]
ALL_PLATFORMS = ["binary_sensor", "climate", "sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Plugwise platform."""
    return True


async def async_setup_entry(hass, entry):
    """Set up Plugwise Smiles from a config entry."""
    websession = async_get_clientsession(hass, verify_ssl=False)

    host = entry.data[CONF_HOST]
    port = 80
    if ":" in host:
        host = entry.data[CONF_HOST].split(":")[0]
        port = int(entry.data[CONF_HOST].split(":")[1])

    api = Smile(
        host=host,
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        port=port,
        websession=websession,
    )

    try:
        connected = await api.connect()

        if not connected:
            _LOGGER.error("Unable to connect to Smile %s", smile_name)
            raise ConfigEntryNotReady

    except Smile.InvalidAuthentication:
        _LOGGER.error("Invalid username or Smile ID")
        return False

    except Smile.PlugwiseError:
        _LOGGER.error("Error while communicating to Smile %s", api.smile_name)
        raise ConfigEntryNotReady

    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while connecting to Smile %s", api.smile_name)
        raise ConfigEntryNotReady

    update_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL[api.smile_type]
        )
    )

    async def async_update_data():
        """Update data via API endpoint."""
        _LOGGER.debug("Updating Smile %s", api.smile_name)
        try:
            async with async_timeout.timeout(60):
                await api.full_update_device()
                _LOGGER.debug("Succesfully updated Smile %s", api.smile_name)
                return True
        except Smile.XMLDataMissingError:
            _LOGGER.debug(
                "Updating Smile failed, expected XML data for %s", api.smile_name
            )
            raise UpdateFailed("Smile update failed")
        except Smile.PlugwiseError:
            _LOGGER.debug(
                "Updating Smile failed, generic failure for %s", api.smile_name
            )
            raise UpdateFailed("Smile update failed")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Smile {api.smile_name}",
        update_method=async_update_data,
        update_interval=update_interval,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    _LOGGER.debug("Async update interval %s", update_interval)

    api.get_all_devices()

    undo_listener = entry.add_update_listener(_update_listener)

    # Migrate to a valid unique_id when needed
    if entry.unique_id is None:
        if api.smile_version[0] != "1.8.0":
            hass.config_entries.async_update_entry(entry, unique_id=api.smile_hostname)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

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

    await hass.async_add_executor_job(setup_hass_services, hass)

    return True


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator.update_interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL)
    )


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

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    coordinator.update_interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL)
    )

def setup_hass_services(hass):
    """Home Assistant services."""

    def delete_notification():
        """Delete the Plugwise Notification."""
        try:
            api.delete_notification()
        except Smile.PlugwiseError:
            _LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s", api.smile_name
            )

    hass.services.register(DOMAIN, SERVICE_DELETE, delete_notification, schema=None)


class SmileGateway(CoordinatorEntity):
    """Represent Smile Gateway."""

    def __init__(self, api, coordinator, name, dev_id):
        """Initialise the gateway."""

        super().__init__(coordinator)
        self._api = api
        self._name = name
        self._dev_id = dev_id

        self._unique_id = None
        self._model = None

        self._entity_name = self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity, if any."""
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        device_information = {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._entity_name,
            "manufacturer": "Plugwise",
        }

        if self._model is not None:
            device_information["model"] = self._model.replace("_", " ").title()

        if self._dev_id != self._api.gateway_id:
            device_information["via_device"] = (DOMAIN, self._api.gateway_id)

        return device_information

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self._async_process_data()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._async_process_data)
        )

    @callback
    def _async_process_data(self):
        """Interpret and process API data."""
        raise NotImplementedError
