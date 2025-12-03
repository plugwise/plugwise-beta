"""DataUpdateCoordinator for Plugwise."""

from datetime import timedelta

from plugwise import GwEntityData, Smile
from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidSetupError,
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

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER

type PlugwiseConfigEntry = ConfigEntry[PlugwiseDataUpdateCoordinator]


class PlugwiseDataUpdateCoordinator(DataUpdateCoordinator[dict[str, GwEntityData]]):
    """Class to manage fetching Plugwise data from single endpoint."""

    _connected: bool = False
    _current_devices: set[str]
    _stored_devices: set[str]
    new_devices: set[str]

    config_entry: PlugwiseConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        cooldown: float,
        config_entry: PlugwiseConfigEntry,
        update_interval: timedelta = timedelta(seconds=60),
    ) -> None:  # pw-beta cooldown
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
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
        self._current_devices = set()
        self._stored_devices = set()
        self.new_devices = set()
        self.update_interval = update_interval

    async def _connect(self) -> None:
        """Connect to the Plugwise Smile.

        Returns a Version object when connection succeeds.
        """
        try:
            version = await self.api.connect()
        except ConnectionFailedError:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="failed_to_connect",
            )
        except InvalidAuthentication:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            )
        except InvalidSetupError:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="invalid_setup",
            )
        except (InvalidXMLError, ResponseError):
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="invalid_xml_data",
            )
        except UnsupportedDeviceError:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="unsupported_firmware",
            )

        self._connected = isinstance(version, Version)
        if self._connected:
            self.update_interval = DEFAULT_SCAN_INTERVAL.get(
                self.api.smile.type, timedelta(seconds=60)
            )  # pw-beta options scan-interval
            if (custom_time := self.config_entry.options.get(CONF_SCAN_INTERVAL)) is not None:
                self.update_interval = timedelta(
                    seconds=int(custom_time)
                )  # pragma: no cover  # pw-beta options

        LOGGER.debug("DUC update interval: %s", self.update_interval)  # pw-beta options

    async def _async_setup(self) -> None:
        """Initialize the update_data process."""
        device_reg = dr.async_get(self.hass)
        device_entries = dr.async_entries_for_config_entry(
            device_reg, self.config_entry.entry_id
        )
        self._stored_devices = {
            identifier[1]
            for device_entry in device_entries
            for identifier in device_entry.identifiers
            if identifier[0] == DOMAIN
        }

    async def _async_update_data(self) -> dict[str, GwEntityData]:
        """Fetch data from Plugwise."""
        if not self._connected:
            await self._connect()
        try:
            data = await self.api.async_update()
        except PlugwiseError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="data_incomplete_or_missing",
            ) from err

        await self._async_add_remove_devices(data)
        LOGGER.debug("%s data: %s", self.api.smile.name, data)
        return data

    async def _async_add_remove_devices(self, data: dict[str, GwEntityData]) -> None:
        """Add new Plugwise devices, remove non-existing devices."""
        # Check for new or removed devices
        set_of_data = set(data)
        self.new_devices = set_of_data - self._current_devices
        current_devices = self._stored_devices if not self._current_devices else self._current_devices
        self._current_devices = set_of_data
        if (current_devices - set_of_data):  # device(s) to remove
            await self._async_remove_devices(data)

    async def _async_remove_devices(self, data: dict[str, GwEntityData]) -> None:
        """Clean registries when removed devices found."""
        device_reg = dr.async_get(self.hass)
        device_list = dr.async_entries_for_config_entry(
            device_reg, self.config_entry.entry_id
        )

        # First find the Plugwise via_device
        gateway_device = device_reg.async_get_device({(DOMAIN, self.api.gateway_id)})
        if gateway_device is None:
            return  # pragma: no cover

        via_device_id = gateway_device.id
        # Then remove the connected orphaned device(s)
        for device_entry in device_list:
            for identifier in device_entry.identifiers:
                if (
                    identifier[0] == DOMAIN
                    and device_entry.via_device_id == via_device_id
                    and identifier[1] not in data
                ):
                    device_reg.async_update_device(
                        device_entry.id, remove_config_entry_id=self.config_entry.entry_id
                    )
                    LOGGER.debug(
                        "Removed %s device/zone %s %s from device_registry",
                        DOMAIN,
                        device_entry.model,
                        identifier[1],
                    )
