"""Provides the Plugwise DataUpdateCoordinator."""
import logging

from async_timeout import timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN
from plugwise.exceptions import PlugwiseException, XMLDataMissingError

_LOGGER = logging.getLogger(__name__)


class PWDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Plugwise API data from a single endpoint."""

    def __init__(self, hass, api, interval):
        """Initialize the coordinator."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=interval
        )
        self._api = api

    async def _async_update_data(self):
        """Update data via API endpoint."""
        try:
            data = await self._api.async_update()
            _LOGGER.debug("Plugwise %s updated", self._api.smile_name)
            _LOGGER.debug("with data: %s", data)
        except XMLDataMissingError as err:
            raise UpdateFailed(
                f"Updating failed, expected XML data for Plugwise {self._api.smile_name}"
            ) from err
        except PlugwiseException as err:
            raise UpdateFailed(
                f"Updating failed for Plugwise {self._api.smile_name}"
            ) from err
        return data
