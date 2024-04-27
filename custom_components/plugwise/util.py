"""Utilities for Plugwise."""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Concatenate, ParamSpec, TypeVar

from plugwise import PlugwiseData
from plugwise.exceptions import PlugwiseException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .const import COORDINATOR, DOMAIN, GATEWAY_ID, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinatorDataUpdateCoordinator
from .entity import PlugwiseEntity

_PlugwiseEntityT = TypeVar("_PlugwiseEntityT", bound=PlugwiseEntity)
_R = TypeVar("_R")
_P = ParamSpec("_P")


def get_coordinator(
    hass: HomeAssistant, config_entry_id: str
) -> PlugwiseDataUpdateCoordinator:
    """Get coordinator for given config entry id."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][config_entry_id][COORDINATOR]
    return coordinator

def plugwise_command(
    func: Callable[Concatenate[_PlugwiseEntityT, _P], Awaitable[_R]]
) -> Callable[Concatenate[_PlugwiseEntityT, _P], Coroutine[Any, Any, _R]]:
    """Decorate Plugwise calls that send commands/make changes to the device.

    A decorator that wraps the passed in function, catches Plugwise errors,
    and requests an coordinator update to update status of the devices asap.
    """

    async def handler(
        self: _PlugwiseEntityT, *args: _P.args, **kwargs: _P.kwargs
    ) -> _R:
        try:
            return await func(self, *args, **kwargs)
        except PlugwiseException as error:
            raise HomeAssistantError(
                f"Error communicating with API: {error}"
            ) from error
        finally:
            await self.coordinator.async_request_refresh()

    return handler

async def cleanup_device_registry(
    hass: HomeAssistant,
    data: PlugwiseData,
    entry: ConfigEntry,
) -> None:
    """Remove deleted devices from device-registry."""
    device_registry = dr.async_get(hass)
    device_entries = dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    )
    # via_device cannot be None, this will result in the deletion
    # of other Plugwise Gateways when present!
    via_device: str = ""
    for device_entry in device_entries:
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
            device_registry.async_remove_device(device_entry.id)
            LOGGER.debug(
                "Removed %s device %s %s from device_registry",
                DOMAIN,
                device_entry.model,
                item[1],
            )
