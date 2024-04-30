"""Diagnostics support for Plugwise."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import (
    AVAILABLE_SCHEDULES,
    COORDINATOR,  # pw-beta
    DEVICES,
    DOMAIN,
    GATEWAY,
    MAC_ADDRESS,
    NONE,
    SELECT_SCHEDULE,
    ZIGBEE_MAC_ADDRESS,
)
from .coordinator import PlugwiseDataUpdateCoordinator

KEYS_TO_REDACT = {
    ATTR_NAME,
    MAC_ADDRESS,
    ZIGBEE_MAC_ADDRESS
}

OFF = "off"

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    data = async_redact_data(coordinator.data.devices, KEYS_TO_REDACT)

    for device in data:
        for key, value in data[device].items():
            if key == AVAILABLE_SCHEDULES:
                for i in range(len(value)):
                    if value[i] not in (OFF, NONE):
                        value[i] = f"**REDACTED_{i}**"

                data[device][key] = value

            if key == SELECT_SCHEDULE and value not in (OFF, NONE):
                j = 0
                for item in data[device][AVAILABLE_SCHEDULES]:
                    if item == data[device][key]:
                        break
                    j += 1

                data[device][key] = f"**REDACTED_{j}**"

    return {GATEWAY: coordinator.data.gateway, DEVICES: data}
