"""Plugwise network/gateway platform."""

import asyncio
import logging
from datetime import timedelta
from typing import Dict

import async_timeout
import voluptuous as vol
from plugwise.smile import Smile
from plugwise.exceptions import (
    InvalidAuthentication,
    PlugwiseException,
    XMLDataMissingError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
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
    COORDINATOR,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    GATEWAY,
    PLATFORMS_GATEWAY,
    PW_TYPE,
    SENSOR_PLATFORMS,
    SERVICE_DELETE,
    UNDO_UPDATE_LISTENER,
)

SERVICE_PRESET_SETPOINT = "set_preset_setpoint"

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plugwise Smiles from a config entry."""
    websession = async_get_clientsession(hass, verify_ssl=False)

    # When migrating from Core to beta, add the username to ConfigEntry
    entry_updates = {}
    try:
        username = entry.data[CONF_USERNAME]
    except KeyError:
        username = DEFAULT_USERNAME
        data = {**entry.data}
        data.update({"username": username})
        entry_updates["data"] = data

    if entry_updates:
        hass.config_entries.async_update_entry(entry, **entry_updates)

    api = Smile(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        timeout=30,
        websession=websession,
    )

    try:
        connected = await api.connect()

        if not connected:
            _LOGGER.error("Unable to connect to Smile %s", api.smile_name)
            raise ConfigEntryNotReady

    except InvalidAuthentication:
        _LOGGER.error("Invalid username or Smile ID")
        return False

    except PlugwiseException as err:
        _LOGGER.error("Error while communicating to Smile %s", api.smile_name)
        raise ConfigEntryNotReady from err

    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout while connecting to Smile %s", api.smile_name)
        raise ConfigEntryNotReady from err

    update_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL[api.smile_type]
        )
    )

    async def async_update_data_gw():
        """Update data via API endpoint."""
        _LOGGER.debug("Updating Smile %s", api.smile_name)
        try:
            async with async_timeout.timeout(update_interval.seconds):
                await api.full_update_device()
                _LOGGER.debug("Successfully updated Smile %s", api.smile_name)
                return True
        except XMLDataMissingError as err:
            _LOGGER.debug(
                "Updating Smile failed, expected XML data for %s", api.smile_name
            )
            raise UpdateFailed("Smile update failed") from err
        except PlugwiseException as err:
            _LOGGER.debug(
                "Updating Smile failed, generic failure for %s", api.smile_name
            )
            raise UpdateFailed("Smile update failed") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Smile {api.smile_name}",
        update_method=async_update_data_gw,
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
        API: api,
        COORDINATOR: coordinator,
        PW_TYPE: GATEWAY,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    _LOGGER.debug("Gateway is %s", api.gateway_id)

    _LOGGER.debug("Gateway software version is %s", api.smile_version)
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

    platforms = PLATFORMS_GATEWAY
    if single_master_thermostat is None:
        platforms = SENSOR_PLATFORMS

    async def delete_notification(self):
        """Service: delete the Plugwise Notification."""
        _LOGGER.debug("Service delete PW Notification called for %s", api.smile_name)
        try:
            deleted = await api.delete_notification()
            _LOGGER.debug("PW Notification deleted: %s", deleted)
        except PlugwiseException:
            _LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s", api.smile_name
            )

    async def set_preset_setpoint(self, loc_name, pr_name, s_type, s_point):
        """Service: delete the Plugwise Notification."""
        _LOGGER.debug("Service set Preset Setpoint called for %s", api.smile_name)
        try:
            await api.set_preset_setpoint(loc_name, pr_name, s_type, s_point)
            _LOGGER.debug("%s Preset %s setpoint updated to %s C", loc_name, s_type, s_point )
        except PlugwiseException:
            _LOGGER.debug(
                "Failed to update the %s Preset %s setpoint", loc_name, s_type
            )

    for component in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
        if component == "climate":
            hass.services.async_register(
                DOMAIN, SERVICE_DELETE, delete_notification, schema=vol.Schema({})
            )
            hass.services.async_register(
                DOMAIN, SERVICE_PRESET_SETPOINT, set_preset_setpoint, schema=vol.Schema({})
            )
    return True


async def async_unload_entry_gw(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS_GATEWAY
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

    def __init__(self, api, coordinator, name, dev_id):
        """Initialise the gateway."""
        super().__init__(coordinator)

        self._coordinator = coordinator
        self._name = name

        self._api = api
        self._dev_id = dev_id
        self._entity_name = self._name
        self._model = None
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
