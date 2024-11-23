"""DataUpdateCoordinator for Plugwise."""

from datetime import timedelta

from plugwise import PlugwiseData, Smile
from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidXMLError,
    PlugwiseError,
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
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from packaging.version import Version

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, GATEWAY_ID, LOGGER


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
            # Upstream check correct progress for adjusting
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
            password=self.config_entry.data[CONF_PASSWORD],
            port=self.config_entry.data[CONF_PORT],
            username=self.config_entry.data[CONF_USERNAME],
            websession=async_get_clientsession(hass, verify_ssl=False),
        )
        self._current_devices: set[str] = set()
        self._current_zones: set[str] = set()
        self.new_devices: set[str] = set()
        self.new_zones: set[str] = set()
        self.update_interval = update_interval

    async def _connect(self) -> None:
        """Connect to the Plugwise Smile."""
        version = await self.api.connect()
        self._connected = isinstance(version, Version)
        if self._connected:
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
        data = PlugwiseData(devices={}, gateway={}, zones={})
        try:
            if not self._connected:
                await self._connect()
            data = await self.api.async_update()
        except ConnectionFailedError as err:
            raise UpdateFailed("Failed to connect") from err
        except InvalidAuthentication as err:
            raise ConfigEntryError("Authentication failed") from err
        except (InvalidXMLError, ResponseError) as err:
            raise UpdateFailed(
                f"Invalid XML data or error from Plugwise device: {err}"
            ) from err
        except PlugwiseError as err:
            raise UpdateFailed("Data incomplete or missing") from err
        except UnsupportedDeviceError as err:
            raise ConfigEntryError("Device with unsupported firmware") from err
        else:
            LOGGER.debug(f"{self.api.smile_name} data: %s", data)
            await self.async_add_remove_devices_zones(data, self.config_entry)

        return data

    async def async_add_remove_devices_zones(self, data: PlugwiseData, entry: ConfigEntry) -> None:
        """Add new Plugwise devices, remove non-existing devices."""
        # Check for new or removed devices
        self.new_devices = set(data.devices) - self._current_devices
        self.new_zones = set(data.zones) - self._current_zones
        removed_devices = self._current_devices - set(data.devices)
        removed_zones = self._current_zones - set(data.zones)
        self._current_devices = set(data.devices)
        self._current_zones = set(data.zones)

        if removed_devices:
            await self.async_remove_devices(data, entry)
        # if removed_zones:
            # await self.async_remove_zones(data, entry)

    async def async_remove_devices(self, data: PlugwiseData, entry: ConfigEntry) -> None:
        """Clean registries when removed devices found."""
        device_reg = dr.async_get(self.hass)
        device_list = dr.async_entries_for_config_entry(
            device_reg, self.config_entry.entry_id
        )

        # First find the Plugwise via_device
        gateway_device = device_reg.async_get_device({(DOMAIN, data.gateway[GATEWAY_ID])})
        if gateway_device is not None:
            via_device_id = gateway_device.id

        # Then remove the connected orphaned device(s)
        for device_entry in device_list:
            for identifier in device_entry.identifiers:
                if identifier[0] == DOMAIN:
                    if (
                        device_entry.via_device_id == via_device_id
                        and identifier[1] not in data.devices
                    ):
                        device_reg.async_update_device(
                            device_entry.id, remove_config_entry_id=entry.entry_id
                        )
                        LOGGER.debug(
                            "Removed %s device %s %s from device_registry",
                            DOMAIN,
                            device_entry.model,
                            identifier[1],
                        )
