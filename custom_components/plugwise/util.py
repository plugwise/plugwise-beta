"""Utilities for Plugwise."""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Concatenate, ParamSpec, TypeVar

from plugwise.exceptions import PlugwiseException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN, LOGGER, UNIQUE_IDS
from .entity import PlugwiseEntity

_PlugwiseEntityT = TypeVar("_PlugwiseEntityT", bound=PlugwiseEntity)
_R = TypeVar("_R")
_P = ParamSpec("_P")


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


@callback
def _async_cleanup_registry_entries(
    hass: HomeAssistant,
    entry: ConfigEntry,
    entry_id: str
) -> None:
    """Remove extra entities that are no longer part of the integration."""
    entity_registry = er.async_get(hass)
    dev_registry = dr.async_get(hass)
    current_unique_ids = hass.data[DOMAIN][entry_id][UNIQUE_IDS]

    existing_entries = er.async_entries_for_config_entry(entity_registry, entry_id)
    entities = {
        (entity.domain, entity.unique_id): entity.entity_id
        for entity in existing_entries
    }

    LOGGER.debug("HOI current: %s", current_unique_ids)
    LOGGER.debug("HOI entities: %s", set(entities.keys()))
    extra_entities = set(entities.keys()).difference(current_unique_ids)
    LOGGER.debug("HOI extra: %s", extra_entities)
    if not extra_entities:
        return

    for entity in extra_entities:
        if entity_registry.async_is_registered(entities[entity]):
            entity_registry.async_remove(entities[entity])
            device = dev_registry.async_get_device(
                identifiers={(DOMAIN, entities[entity].device_id)}
            )
            if device:
                dev_registry.async_update_device(
                    device.id, remove_config_entry_id=entry.entry_id
                )

    LOGGER.debug(
        ("Clean-up of Plugwise entities: %s entities removed for config entry %s"),
        len(extra_entities),
        entry_id,
    )
