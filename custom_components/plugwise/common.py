"""Common functions for Plugwise integration."""

from homeassistant.core import HomeAssistant

from .const import COORDINATOR, DOMAIN
from .coordinator import PlugwiseDataUpdateCoordinator


def get_coordinator(
    hass: HomeAssistant, config_entry_id: str
) -> PlugwiseDataUpdateCoordinator:
    """Get coordinator for given config entry id."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][config_entry_id][
        COORDINATOR
    ]

    return coordinator
