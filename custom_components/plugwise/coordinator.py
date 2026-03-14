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

from .const import (
    DEFAULT_UPDATE_INTERVAL,
    DEV_CLASS,
    DOMAIN,
    FIRMWARE,
    LOGGER,
    P1_UPDATE_INTERVAL,
    SWITCH_GROUPS,
)

type PlugwiseConfigEntry = ConfigEntry[PlugwiseDataUpdateCoordinator]


class PlugwiseDataUpdateCoordinator(DataUpdateCoordinator[dict[str, GwEntityData]]):
    """Class to manage fetching Plugwise data from single endpoint."""

    config_entry: PlugwiseConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        cooldown: float,
        config_entry: PlugwiseConfigEntry,
    ) -> None:  # pw-beta cooldown
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            # Core directly updates from const's DEFAULT_SCAN_INTERVAL
            # Upstream check correct progress for adjusting
            update_interval=DEFAULT_UPDATE_INTERVAL,
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
        self._connected: bool = False
        self._current_devices: set[str] = set()
        self._firmware_list: dict[str, str | None] = {}
        self._stored_devices: set[str] = set()
        self.new_devices: set[str] = set()

    async def _connect(self) -> None:
        """Connect to the Plugwise Smile.

        A Version object is received when the connection succeeds.
        """
        version = await self.api.connect()
        self._connected = isinstance(version, Version)
        if self._connected:
            if self.api.smile.type == "power":
                self.update_interval = P1_UPDATE_INTERVAL
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
        for device_entry in device_entries:
            firmware = device_entry.sw_version
            for identifier in device_entry.identifiers:
                if identifier[0] == DOMAIN:
                    device_id = identifier[1]
                    self._firmware_list[device_id] = firmware
                    self._stored_devices.add(device_id)

    async def _async_update_data(self) -> dict[str, GwEntityData]:
        """Fetch data from Plugwise."""
        try:
            if not self._connected:
                await self._connect()
            data = await self.api.async_update()
        except ConnectionFailedError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="failed_to_connect",
            ) from err
        except InvalidAuthentication as err:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from err
        except InvalidSetupError as err:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="invalid_setup",
            ) from err
        except (InvalidXMLError, ResponseError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="response_error",
            ) from err
        except PlugwiseError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="data_incomplete_or_missing",
            ) from err
        except UnsupportedDeviceError as err:
            raise ConfigEntryError(
                translation_domain=DOMAIN,
                translation_key="unsupported_firmware",
            ) from err

        LOGGER.debug("%s data: %s", self.api.smile.name, data)
        await self._add_remove_devices(data)
        await self._update_device_firmware(data)
        return data

    async def _add_remove_devices(self, data: dict[str, GwEntityData]) -> None:
        """Add new Plugwise devices, remove non-existing devices."""
        # Block switch-groups, use HA group helper instead to create switch-groups
        for device_id, device in data.copy().items():
            if device.get(DEV_CLASS) in SWITCH_GROUPS:
                data.pop(device_id)

        # Collect new or removed devices,
        # 'new_devices' contains all devices present in 'data' at init ('self._current_devices' is empty)
        # this is required for the initialization of the available platform entities.
        set_of_data = set(data)
        self.new_devices = set_of_data - self._current_devices
        for device_id in self.new_devices:
            self._firmware_list.setdefault(device_id, data[device_id].get(FIRMWARE))

        current_devices = self._stored_devices if not self._current_devices else self._current_devices
        self._current_devices = set_of_data
        if removed_devices := (current_devices - set_of_data):  # device(s) to remove
            await self._remove_devices(removed_devices)

    async def _remove_devices(self, removed_devices: set[str]) -> None:
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
                    and identifier[1] in removed_devices
                ):
                    device_reg.async_update_device(
                        device_entry.id, remove_config_entry_id=self.config_entry.entry_id
                    )
                    self._firmware_list.pop(identifier[1], None)
                    LOGGER.debug(
                        "Removed %s device/zone %s %s from device_registry",
                        DOMAIN,
                        device_entry.model,
                        identifier[1],
                    )
                    break

    async def _update_device_firmware(self, data: dict[str, GwEntityData]) -> None:
        """Sync device_registry sw_version with API firmware changes."""
        for device_id, device in data.items():
            if device_id not in self._firmware_list:
                continue
            if (new_firmware := device.get(FIRMWARE)) != self._firmware_list[device_id]:
                await self._update_firmware_in_dr(device_id, new_firmware)
                self._firmware_list[device_id] = new_firmware

    async def _update_firmware_in_dr(self, device_id: str, firmware: str | None) -> None:
        """Update device sw_version in device_registry."""
        device_reg = dr.async_get(self.hass)
        device_entry = device_reg.async_get_device({(DOMAIN, device_id)})
        if device_entry is None:
            return

        device_reg.async_update_device(device_entry.id, sw_version=firmware)
        LOGGER.debug(
            "Updated device firmware for %s %s %s",
            DOMAIN,
            device_entry.model,
            device_id,
        )
