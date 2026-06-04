"""Services for the Plugwise-beta integration."""

from plugwise.exceptions import PlugwiseError
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv, service

from .const import (
    CONF_CONFIG_ENTRY,
    DOMAIN,
    LOGGER,
    SERVICE_DELETE,  # pw-beta delete_notifications
)
from .coordinator import PlugwiseConfigEntry


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Plugwise-beta services."""

    async def delete_notification(
        call: ServiceCall,
    ) -> None:  # pragma: no cover  # pw-beta: HA service - delete_notification
        """Service: delete the Plugwise Notification."""

        entry: PlugwiseConfigEntry = service.async_get_config_entry(
            call.hass, DOMAIN, call.data[CONF_CONFIG_ENTRY]
        )
        coordinator = entry.runtime_data

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

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE,
        delete_notification,
        schema=vol.Schema(
            {vol.Required(CONF_CONFIG_ENTRY): cv.string}
        ),
    )
