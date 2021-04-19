"""Plugwise network/gateway platform."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import async_timeout
import voluptuous as vol
from plugwise.exceptions import (
    InvalidAuthentication,
    PlugwiseException,
    XMLDataMissingError,
)
from plugwise.gw_device import GWDevice
from plugwise.smile import Smile

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from .const import (
    API,
    CLIMATE_DOMAIN,
    COORDINATOR,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    GATEWAY,
    GATEWAY_PLATFORMS,
    PW_TYPE,
    SENSOR_PLATFORMS,
    SERVICE_DELETE,
    SMILE,
    UNDO_UPDATE_LISTENER,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry_gw(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up Plugwise Smiles from a config entry."""
    websession = async_get_clientsession(hass, verify_ssl=False)

    # When migrating from Core to beta, add the username to ConfigEntry
    entry_updates = {}
    if CONF_USERNAME not in entry.data:
        data = {**entry.data}
        data.update({CONF_USERNAME: DEFAULT_USERNAME})
        entry_updates["data"] = data

    if entry_updates:
        hass.config_entries.async_update_entry(entry, **entry_updates)

    smile = GWDevice(
        host=entry.data[CONF_HOST],
        password=entry.data[CONF_PASSWORD],
        websession=websession,
    )

    try:
        api = await smile.discover()
        if not api:
            _LOGGER.error("Unable to connect to the Smile/Stretch")
            raise ConfigEntryNotReady
    except InvalidAuthentication:
        _LOGGER.error("Invalid username or Smile ID")
        return False
    except PlugwiseException as err:
        _LOGGER.error("Error while communicating to the Smile/Stretch")
        raise ConfigEntryNotReady from err
    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout while connecting to the Smile/Stretch")
        raise ConfigEntryNotReady from err

    # Migrate to a valid unique_id when needed
    if entry.unique_id is None:
        if smile.firmware_version != "1.8.0":
            hass.config_entries.async_update_entry(entry, unique_id=smile.hostname)

    update_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL[smile.s_type]
        )
    )

    async def async_update_data_gw():
        """Update data via API endpoint."""
        _LOGGER.debug(f"Updating {smile.friendly_name}")
        try:
            async with async_timeout.timeout(update_interval.seconds):
                await api.update_device()
                _LOGGER.debug(f"Successfully updated {smile.friendly_name}")
                return True
        except XMLDataMissingError as err:
            _LOGGER.debug(
                f"Updating Smile failed, expected XML data for {smile.friendly_name}"
            )
            raise UpdateFailed("Smile update failed") from err
        except PlugwiseException as err:
            _LOGGER.debug(
                f"Updating failed, generic failure for {smile.friendly_name}"
            )
            raise UpdateFailed("Smile update failed") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{smile.friendly_name}",
        update_method=async_update_data_gw,
        update_interval=update_interval,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(_update_listener)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        API: api,
        SMILE: smile,
        COORDINATOR: coordinator,
        PW_TYPE: GATEWAY,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    #api.get_all_devices()
    _LOGGER.debug(f"Gateway is {smile.gateway_id}")
    _LOGGER.debug(f"Gateway software version is {smile.firmware_version}")
    _LOGGER.debug(f"Appliances is {api.appl_data}")
    _LOGGER.debug(f"Locations (matched) are {api.thermo_locs}")

    _LOGGER.debug(f"Single master thermostat = {smile.single_master_thermostat}")

    platforms = GATEWAY_PLATFORMS
    if smile.single_master_thermostat is None:
        platforms = SENSOR_PLATFORMS

    async def delete_notification(self):
        """Service: delete the Plugwise Notification."""
        _LOGGER.debug(f"Service delete PW Notification called for {smile.friendly_name}")
        try:
            deleted = await api.delete_notification()
            _LOGGER.debug(f"PW Notification deleted: {deleted}")
        except PlugwiseException:
            _LOGGER.debug(
                f"Failed to delete the Plugwise Notification for {smile.friendly_name}"
            )

    for component in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
        if component == CLIMATE_DOMAIN:
            hass.services.async_register(
                DOMAIN, SERVICE_DELETE, delete_notification, schema=vol.Schema({})
            )

    return True


async def async_unload_entry_gw(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in GATEWAY_PLATFORMS
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


class SmileGateway(CoordinatorEntity):
    """Represent Smile Gateway."""

    def __init__(self, coordinator, dev_id, smile, model, vendor, fw):
        """Initialise the gateway."""
        super().__init__(coordinator)

        self._coordinator = coordinator
        self._dev_id = dev_id
        self._fw_version = fw
        self._manufacturer = vendor
        self._model = model
        self._name = None
        self._smile = smile
        self._unique_id = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def name(self):
        """Return the name of the entity, if any."""
        return self._name

    @property
    def device_info(self) -> dict[str, any]:
        """Return the device information."""
        device_information = {
            "identifiers": {(DOMAIN, self._dev_id)},
            "name": self._name,
            "manufacturer": self._manufacturer,
            "model": self._model,
            "sw_version": self._fw_version,
        }

        if self._dev_id != self._smile.gateway_id:
            device_information["via_device"] = (DOMAIN, self._smile.gateway_id)
        else:
            device_information["name"] = f"{self._smile.friendly_name}"

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
