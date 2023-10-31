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
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_USERNAME, DOMAIN, LOGGER


def cleanup_device_registry(
    hass: HomeAssistant,
    api: Smile,
) -> None:
    """Remove deleted devices from device-registry."""
    device_registry = dr.async_get(hass)
    via_id_list: list[list[str]] = []
    # Find the device_entry-id's of the available Plugwise Gateway's
    for device_entry in list(device_registry.devices.values()):
        if device_entry.manufacturer == "Plugwise" and device_entry.model == "Gateway":
            for item in device_entry.identifiers:
                via_id_list.append([device_entry.id, item[1]])

    # Process the devices connected to the active Gateway
    for via_id in via_id_list:
        if via_id[1] != api.gateway_id:
            continue  # pragma: no cover

        for dev_id, device_entry in list(device_registry.devices.items()):
            if device_entry.via_device_id == via_id[0]:
                for item in device_entry.identifiers:
                    if item[0] == DOMAIN and item[1] in api.device_list:
                        continue

                    # device_registry.async_remove_device(dev_id)
                    LOGGER.debug(
                        "Removed device %s %s %s from device_registry",
                        DOMAIN,
                        device_entry.model,
                        dev_id,
                    )


class PlugwiseDataUpdateCoordinator(DataUpdateCoordinator[PlugwiseData]):
    """Class to manage fetching Plugwise data from single endpoint."""

    _connected: bool = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
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
            host=entry.data[CONF_HOST],
            username=entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
            password=entry.data[CONF_PASSWORD],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            timeout=30,
            websession=async_get_clientsession(hass, verify_ssl=False),
        )
        self.hass = hass
        self._entry = entry
        self._unavailable_logged = False
        self.current_unique_ids: set[tuple[str, str]] = {("dummy", "dummy_id")}
        self.update_interval = update_interval

    async def _connect(self) -> None:
        """Connect to the Plugwise Smile."""
        self._connected = await self.api.connect()
        self.api.get_all_devices()

        self.update_interval = DEFAULT_SCAN_INTERVAL.get(
            self.api.smile_type, timedelta(seconds=60)
        )  # pw-beta options scan-interval
        if (custom_time := self._entry.options.get(CONF_SCAN_INTERVAL)) is not None:
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

        # Clean-up removed devices
        cleanup_device_registry(self.hass, self.api)

        return data
