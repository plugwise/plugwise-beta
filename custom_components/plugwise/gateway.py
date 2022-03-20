"""Plugwise network/gateway platform."""
from __future__ import annotations

import asyncio
import aiohttp
from datetime import timedelta
from typing import Any
import voluptuous as vol

from plugwise.exceptions import InvalidAuthentication, PlugwiseException
from plugwise.smile import Smile

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import RegistryEntry, async_migrate_entries

from .const import (
    COORDINATOR,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    GATEWAY,
    LOGGER,
    PLATFORMS_GATEWAY,
    PW_TYPE,
    SERVICE_DELETE,
    UNDO_UPDATE_LISTENER,
)
from .coordinator import PlugwiseDataUpdateCoordinator


async def async_setup_entry_gw(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plugwise Smiles from a config entry."""
    await async_migrate_entries(hass, entry.entry_id, async_migrate_entity_entry)

    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(
        host=entry.data[CONF_HOST],
        username=entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
        password=entry.data[CONF_PASSWORD],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        timeout=30,
        websession=websession,
    )

    try:
        await api.connect()
    except InvalidAuthentication:
        LOGGER.error("Invalid username or Smile ID")
        return False
    except PlugwiseException as err:
        raise ConfigEntryNotReady(
            "Error while communicating to the Plugwise Smile"
        ) from err
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady("Failed connecting to the Plugwise Smile") from err
    except asyncio.TimeoutError as err:
        raise ConfigEntryNotReady(
            "Timeout while connecting to the Plugwise Smile"
        ) from err

    api.get_all_devices()

    if entry.unique_id is None and api.smile_version[0] != "1.8.0":
        hass.config_entries.async_update_entry(entry, unique_id=api.smile_hostname)

    # pw-beta refresh-interval
    update_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL[api.smile_type]
        )
    )
    LOGGER.debug("DUC update iterval: %s", update_interval)

    # pw-beta - update_interval as extra
    coordinator = PlugwiseDataUpdateCoordinator(hass, api, update_interval)
    await coordinator.async_config_entry_first_refresh()

    # pw-beta
    undo_listener = entry.add_update_listener(_update_listener)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        COORDINATOR: coordinator,  # pw-beta
        PW_TYPE: GATEWAY,  # pw-beta
        UNDO_UPDATE_LISTENER: undo_listener,  # pw-beta
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, str(api.gateway_id))},
        manufacturer="Plugwise",
        name=entry.title,
        model=f"Smile {api.smile_name}",
        sw_version=api.smile_version[0],
    )

    # pw-beta: HA service - delete_notification
    async def delete_notification(self):
        """Service: delete the Plugwise Notification."""
        LOGGER.debug("Service delete PW Notification called for %s", api.smile_name)
        try:
            deleted = await api.delete_notification()
            LOGGER.debug("PW Notification deleted: %s", deleted)
        except PlugwiseException:
            LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s", api.smile_name
            )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS_GATEWAY)

    # pw-beta
    for component in PLATFORMS_GATEWAY:
        if component == Platform.CLIMATE:
            hass.services.async_register(
                DOMAIN, SERVICE_DELETE, delete_notification, schema=vol.Schema({})
            )

    return True


# pw-beta
async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry_gw(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS_GATEWAY
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


@callback
def async_migrate_entity_entry(entry: RegistryEntry) -> dict[str, Any] | None:
    """Migrate Plugwise entity entries.

    - Migrates unique ID from old relay switches to the new unique ID
    """
    if entry.domain == BINARY_SENSOR_DOMAIN and "auxiliary" in entry.unique_id:
        return {"new_unique_id": entry.unique_id.replace("-auxiliary", "-opentherm")}

    if entry.domain == SWITCH_DOMAIN and entry.unique_id.endswith("-plug"):
        return {"new_unique_id": entry.unique_id.replace("-plug", "-relay")}

    if entry.domain == SENSOR_DOMAIN and entry.unique_id.endswith("-outdoor_temperature"):
        return {"new_unique_id": entry.unique_id.replace("-outdoor_temperature", "-outdoor_air_temperature")}

    # No migration needed
    return None
