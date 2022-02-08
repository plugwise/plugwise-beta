"""DataUpdateCoordinator for Plugwise."""
import logging

from datetime import timedelta
from typing import Any, NamedTuple

from plugwise import Smile
from plugwise.exceptions import PlugwiseException, XMLDataMissingError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class PlugwiseData(NamedTuple):
    """Plugwise data stored in the DataUpdateCoordinator."""

    gateway: dict[str, Any]
    devices: dict[str, dict[str, Any]]


class PlugwiseDataUpdateCoordinator(DataUpdateCoordinator[PlugwiseData]):
    """Class to manage fetching Plugwise data from single endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: Smile,
        interval: datetime.timedelta
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=api.smile_name or DOMAIN,
            update_interval=interval
        )
        self.api = api

    async def _async_update_data(self) -> PlugwiseData:
        """Fetch data from Plugwise."""
        try:
            data = await self.api.async_update()
            LOGGER.debug("Plugwise %s updated", self.api.smile_name)
            LOGGER.debug("with data: %s", data)
        except XMLDataMissingError as err:
            raise UpdateFailed(
                f"No XML data received for: {self.api.smile_name}"
            ) from err
        except PlugwiseException as err:
            raise UpdateFailed(f"Updated failed for: {self.api.smile_name}") from err
        return PlugwiseData(*data)