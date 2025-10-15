"""Plugwise platform for Home Assistant Core."""

from __future__ import annotations

from typing import Any

from plugwise.exceptions import PlugwiseError
import voluptuous as vol  # pw-beta delete_notification

from homeassistant.const import CONF_TIMEOUT, Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,  # pw-beta delete_notification
    callback,
)
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import (
    CONF_REFRESH_INTERVAL,  # pw-beta options
    DOMAIN,
    LOGGER,
    PLATFORMS,
    SERVICE_DELETE,  # pw-beta delete_notifications
)
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: PlugwiseConfigEntry) -> bool:
    """Set up Plugwise from a config entry."""
    await er.async_migrate_entries(hass, entry.entry_id, async_migrate_entity_entry)

    cooldown = 1.5  # pw-beta frontend refresh-interval
    if (
        custom_refresh := entry.options.get(CONF_REFRESH_INTERVAL)
    ) is not None:  # pragma: no cover
        cooldown = custom_refresh
    LOGGER.debug("DUC cooldown interval: %s", cooldown)

    coordinator = PlugwiseDataUpdateCoordinator(
        hass, cooldown, entry
    )  # pw-beta - cooldown, update_interval as extra
    await coordinator.async_config_entry_first_refresh()

    await async_migrate_sensor_entities(hass, coordinator)

    entry.runtime_data = coordinator

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, str(coordinator.api.gateway_id))},
        manufacturer="Plugwise",
        model=coordinator.api.smile.model,
        model_id=coordinator.api.smile.model_id,
        name=coordinator.api.smile.name,
        sw_version=str(coordinator.api.smile.version),
    )  # required for adding the entity-less P1 Gateway

    async def delete_notification(
        call: ServiceCall,
    ) -> None:  # pragma: no cover  # pw-beta: HA service - delete_notification
        """Service: delete the Plugwise Notification."""
        LOGGER.debug(
            "Service delete PW Notification called for %s",
            coordinator.api.smile.name,
        )
        try:
            await coordinator.api.delete_notification()
            LOGGER.debug("PW Notification deleted")
        except PlugwiseError:
            LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s",
                coordinator.api.smile.name,
            )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))  # pw-beta options_flow
    for component in PLATFORMS:  # pw-beta delete_notification
        if component == Platform.BINARY_SENSOR:
            hass.services.async_register(
                DOMAIN, SERVICE_DELETE, delete_notification, schema=vol.Schema({})
            )

    return True

async def update_listener(
    hass: HomeAssistant, entry: PlugwiseConfigEntry
) -> None:  # pragma: no cover  # pw-beta
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: PlugwiseConfigEntry) -> bool:
    """Unload Plugwise."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

@callback
def async_migrate_entity_entry(entry: er.RegistryEntry) -> dict[str, Any] | None:
    """Migrate Plugwise entity entries.

    - Migrates old unique ID's from old binary_sensors and switches to the new unique ID's
    """
    if entry.domain == Platform.BINARY_SENSOR and entry.unique_id.endswith(
        "-slave_boiler_state"
    ):
        return {
            "new_unique_id": entry.unique_id.replace(
                "-slave_boiler_state", "-secondary_boiler_state"
            )
        }
    if entry.domain == Platform.SENSOR and entry.unique_id.endswith(
        "-relative_humidity"
    ):
        return {
            "new_unique_id": entry.unique_id.replace("-relative_humidity", "-humidity")
        }
    if entry.domain == Platform.SWITCH and entry.unique_id.endswith("-plug"):
        return {"new_unique_id": entry.unique_id.replace("-plug", "-relay")}

    # No migration needed
    return None

async def async_migrate_sensor_entities(
    hass: HomeAssistant,
    coordinator: PlugwiseDataUpdateCoordinator,
) -> None:
    """Migrate Sensors if needed."""
    ent_reg = er.async_get(hass)

    # Migrate opentherm_outdoor_temperature
    # to opentherm_outdoor_air_temperature sensor
    for device_id, device in coordinator.data.items():
        if device["dev_class"] != "heater_central":
            continue

        old_unique_id = f"{device_id}-outdoor_temperature"
        if entity_id := ent_reg.async_get_entity_id(
            Platform.SENSOR, DOMAIN, old_unique_id
        ):
            new_unique_id = f"{device_id}-outdoor_air_temperature"
            # Upstream remove LOGGER debug
            ent_reg.async_update_entity(entity_id, new_unique_id=new_unique_id)

# pw-beta only - revert adding CONF_TIMEOUT to config_entry in v0.53.3
async def async_migrate_entry(hass: HomeAssistant, entry: PlugwiseConfigEntry) -> bool:
    """Migrate back to v1.1 config entry."""
    if entry.version > 1:
        # This means the user has downgraded from a future version
        return False  # pragma: no cover

    if entry.version == 1 and entry.minor_version == 2:
        new_data = {**entry.data}
        new_data.pop(CONF_TIMEOUT)
        hass.config_entries.async_update_entry(
            entry, data=new_data, minor_version=1, version=1
        )

    LOGGER.debug(
        "Migration to version %s.%s successful",
        entry.version,
        entry.minor_version,
    )

    return True
