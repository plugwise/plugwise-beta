"""Plugwise platform for Home Assistant Core."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from plugwise.exceptions import PlugwiseError

from .const import (
    COORDINATOR,
    DOMAIN,
    GATEWAY,
    LOGGER,
    PLATFORMS_GATEWAY,
    SERVICE_DELETE,
    UNDO_UPDATE_LISTENER,
)
from .const import CONF_REFRESH_INTERVAL  # pw-beta options
from .coordinator import PlugwiseDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plugwise Smiles from a config entry."""
    await er.async_migrate_entries(hass, entry.entry_id, async_migrate_entity_entry)

    cooldown = 1.5  # pw-beta frontend refresh-interval
    if (
        custom_refresh := entry.options.get(CONF_REFRESH_INTERVAL)
    ) is not None:  # pragma: no cover
        cooldown = custom_refresh
    LOGGER.debug("DUC cooldown interval: %s", cooldown)

    coordinator = PlugwiseDataUpdateCoordinator(
        hass, entry, cooldown
    )  # pw-beta - cooldown, update_interval as extra
    await coordinator.async_config_entry_first_refresh()
    # Migrate a changed sensor unique_id
    migrate_sensor_entities(hass, coordinator)

    undo_listener = entry.add_update_listener(_update_listener)  # pw-beta

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        COORDINATOR: coordinator,  # pw-beta
        UNDO_UPDATE_LISTENER: undo_listener,  # pw-beta
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, str(coordinator.api.gateway_id))},
        manufacturer="Plugwise",
        model=coordinator.api.smile_model,
        name=coordinator.api.smile_name,
        sw_version=coordinator.api.smile_version[0],
    )

    async def delete_notification(
        self,
    ):  # pragma: no cover  # pw-beta: HA service - delete_notification
        """Service: delete the Plugwise Notification."""
        LOGGER.debug(
            "Service delete PW Notification called for %s", coordinator.api.smile_name
        )
        try:
            deleted = await coordinator.api.delete_notification()
            LOGGER.debug("PW Notification deleted: %s", deleted)
        except PlugwiseError:
            LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s",
                coordinator.api.smile_name,
            )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_GATEWAY)

    for component in PLATFORMS_GATEWAY:  # pw-beta
        if component == Platform.BINARY_SENSOR:
            hass.services.async_register(
                DOMAIN, SERVICE_DELETE, delete_notification, schema=vol.Schema({})
            )

    return True


async def _update_listener(
    hass: HomeAssistant, entry: ConfigEntry
):  # pragma: no cover  # pw-beta
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS_GATEWAY
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


@callback
def async_migrate_entity_entry(entry: er.RegistryEntry) -> dict[str, Any] | None:
    """Migrate Plugwise entity entries.

    - Migrates unique ID from old relay switches to the new unique ID
    """
    if entry.domain == SWITCH_DOMAIN and entry.unique_id.endswith("-plug"):
        return {"new_unique_id": entry.unique_id.replace("-plug", "-relay")}

    # No migration needed
    return None


def migrate_sensor_entities(
    hass: HomeAssistant,
    coordinator: PlugwiseDataUpdateCoordinator,
) -> None:
    """Migrate Sensors if needed."""
    ent_reg = er.async_get(hass)

    # Migrate opentherm_outdoor_temperature  # pw-beta add to Core
    # to opentherm_outdoor_air_temperature sensor
    for device_id, device in coordinator.data.devices.items():
        if device["dev_class"] != "heater_central":  # pw-beta add to Core
            continue

        old_unique_id = f"{device_id}-outdoor_temperature"
        if entity_id := ent_reg.async_get_entity_id(
            Platform.SENSOR, DOMAIN, old_unique_id
        ):
            new_unique_id = f"{device_id}-outdoor_air_temperature"
            ent_reg.async_update_entity(entity_id, new_unique_id=new_unique_id)
