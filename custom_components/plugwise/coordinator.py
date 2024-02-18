"""DataUpdateCoordinator for Plugwise."""
from datetime import timedelta

from plugwise import PlugwiseData, Smile
from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidXMLError,
    ResponseError,
    UnsupportedDeviceError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,  # pw-beta options
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_USERNAME, DOMAIN, LOGGER


class PlugwiseDataUpdateCoordinator(DataUpdateCoordinator[PlugwiseData]):
    """Class to manage fetching Plugwise data from single endpoint."""

    _connected: bool = False

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        cooldown: float,
        update_interval: timedelta = timedelta(seconds=60),
    ) -> None:  # pw-beta cooldown
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            # Core directly updates from const's DEFAULT_SCAN_INTERVAL
            update_interval=update_interval,
            # Don't refresh immediately, give the device time to process
            # the change in state before we query it.
            request_refresh_debouncer=Debouncer(
                hass,
                LOGGER,
                cooldown=cooldown,
                immediate=False,
            ),
        )

        self.api = Smile(
            host=self.config_entry.data[CONF_HOST],
            username=self.config_entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
            password=self.config_entry.data[CONF_PASSWORD],
            port=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT),
            timeout=30,
            websession=async_get_clientsession(hass, verify_ssl=False),
        )
        self._unavailable_logged = False
        self.update_interval = update_interval

    async def _connect(self) -> None:
        """Connect to the Plugwise Smile."""
        self._connected = await self.api.connect()
        self.api.get_all_devices()

        self.update_interval = DEFAULT_SCAN_INTERVAL.get(
            self.api.smile_type, timedelta(seconds=60)
        )  # pw-beta options scan-interval
        if (custom_time := self.config_entry.options.get(CONF_SCAN_INTERVAL)) is not None:
            self.update_interval = timedelta(
                seconds=int(custom_time)
            )  # pragma: no cover  # pw-beta options

        LOGGER.debug("DUC update interval: %s", self.update_interval)  # pw-beta options

    async def _async_update_data(self) -> PlugwiseData:
        """Fetch data from Plugwise."""
        data = PlugwiseData(gateway={}, devices={})

        try:
            if not self._connected:
                await self._connect()
            data = await self.api.async_update()
            LOGGER.debug(f"{self.api.smile_name} data: %s", data)
            if self._unavailable_logged:
                self._unavailable_logged = False
        except InvalidAuthentication as err:
            if not self._unavailable_logged:  # pw-beta add to Core
                self._unavailable_logged = True
                raise ConfigEntryError("Authentication failed") from err
        except (InvalidXMLError, ResponseError) as err:
            if not self._unavailable_logged:  # pw-beta add to Core
                self._unavailable_logged = True
                raise UpdateFailed(
                    "Invalid XML data, or error indication received from the Plugwise Adam/Smile/Stretch"
                ) from err
        except UnsupportedDeviceError as err:
            if not self._unavailable_logged:  # pw-beta add to Core
                self._unavailable_logged = True
                raise ConfigEntryError("Device with unsupported firmware") from err
        except ConnectionFailedError as err:
            if not self._unavailable_logged:  # pw-beta add to Core
                self._unavailable_logged = True
                raise UpdateFailed("Failed to connect") from err

        # Reload when the configuration has changed
        if "config_changed" in data.gateway:
            LOGGER.debug("HOI config has changed")
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

        return data
