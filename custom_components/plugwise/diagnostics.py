"""Diagnostics support for Plugwise."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import (
    COORDINATOR,  # pw-beta
    DOMAIN,
)
from .coordinator import PlugwiseDataUpdateCoordinator

KEYS_TO_REDACT = {
    "available_schedules",
    "mac_address",
    "name",
    "select_schedule",
    "zigbee_mac_address"
}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    data = async_redact_data(coordinator.data.devices, KEYS_TO_REDACT)

    return {"gateway": coordinator.data.gateway, "devices": data}
