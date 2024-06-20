"""DataUpdateCoordinator for Plugwise."""

from collections.abc import Callable
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
from homeassistant.helpers.device_registry import DeviceEntry, DeviceRegistry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    GATEWAY_ID,
    LOGGER,
)


async def cleanup_device_and_entity_registry(
    data: PlugwiseData,
    device_reg: DeviceRegistry,
    device_list: list[DeviceEntry],
    entry: ConfigEntry,
) -> None:
    """Remove deleted devices from device- and entity-registry."""
    if len(device_list) - len(data.devices.keys()) <= 0:
        return

    # via_device cannot be None, this will result in the deletion
    # of other Plugwise Gateways when present!
    via_device: str = ""
    for device_entry in device_list:
        if not device_entry.identifiers:
            continue  # pragma: no cover

        item = list(list(device_entry.identifiers)[0])
        if item[0] != DOMAIN:
            continue  # pragma: no cover

        # First find the Plugwise via_device, this is always the first device
        if item[1] == data.gateway[GATEWAY_ID]:
            via_device = device_entry.id
        elif ( # then remove the connected orphaned device(s)
            device_entry.via_device_id == via_device
            and item[1] not in list(data.devices.keys())
        ):
            device_reg.async_update_device(
                device_entry.id, remove_config_entry_id=entry.entry_id
            )
            LOGGER.debug(
                "Removed %s device %s %s from device_registry",
                DOMAIN,
                device_entry.model,
                item[1],
            )


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
        self._devices_last_update: set[str] = set()
        self.device_list: list[DeviceEntry] = []
        self.new_devices_callbacks: list[Callable[[str], None]] = []
        self.new_devices: bool = False
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
        data = PlugwiseData({}, {})
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
                    "Invalid XML data, or error indication received from the Plugwise Adam/Smile/Stretch"
                ) from err
        except PlugwiseError as err:
                raise UpdateFailed("Data incomplete or missing") from err
        except UnsupportedDeviceError as err:
                raise ConfigEntryError("Device with unsupported firmware") from err
        else:
            LOGGER.debug(f"{self.api.smile_name} data: %s", data)
            device_reg = dr.async_get(self.hass)
            device_list = dr.async_entries_for_config_entry(
                device_reg, self.config_entry.entry_id
            )
            # await cleanup_device_and_entity_registry(
            #     data,
            #     device_reg,
            #     device_list,
            #     self.config_entry
            # )
            self.new_devices = len(data.devices.keys()) - len(self.device_list) > 0
            self.device_list = device_list

        self._async_add_remove_devices(data)
        return data

    def _async_add_remove_devices(self, data: PlugwiseData) -> None:
        """Add new locks, remove non-existing locks."""
        if not self._devices_last_update:
            self._devices_last_update = set(data.devices)

        if (
            current_devices := set(data.devices)
        ) == self._devices_last_update:
            return

        # remove old devices
        # if removed_devices := self._locks_last_update - current_locks:
        #     LOGGER.debug("Removed devices: %s", ", ".join(map(str, removed_locks)))
        #     device_registry = dr.async_get(self.hass)
        #     for device_id in removed_devices:
        #         if device := device_registry.async_get_device(
        #             identifiers={(DOMAIN, str(device_id))}
        #         ):
        #             device_registry.async_update_device(
        #                 device_id=device.id,
        #                 remove_config_entry_id=self.config_entry.entry_id,
        #             )

        # add new devices
        if new_devices := current_devices - self._devices_last_update:
            LOGGER.debug("New Plugwise devices found: %s", new_devices)
            for device_id in new_devices:
                for callback in self.new_devices_callbacks:
                    callback(device_id)

        self._devices_last_update = current_devices
