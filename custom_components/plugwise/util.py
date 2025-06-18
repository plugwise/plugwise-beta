"""Utilities for Plugwise."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Concatenate

from plugwise.exceptions import PlugwiseException

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .entity import PlugwiseEntity

# For reference:
# PlugwiseEntityT = TypeVar("PlugwiseEntityT", bound=PlugwiseEntity)
# _R = TypeVar("_R")
# _P = ParamSpec("_P")


def plugwise_command[PlugwiseEntityT: PlugwiseEntity, **_P, _R](
    func: Callable[Concatenate[PlugwiseEntityT, _P], Awaitable[_R]],
) -> Callable[Concatenate[PlugwiseEntityT, _P], Coroutine[Any, Any, _R]]:
    """Decorate Plugwise calls that send commands/make changes to the device.

    A decorator that wraps the passed in function, catches Plugwise errors,
    and requests an coordinator update to update status of the devices asap.
    """

    async def handler(
        self: PlugwiseEntityT, *args: _P.args, **kwargs: _P.kwargs
    ) -> _R:
        try:
            return await func(self, *args, **kwargs)
        except PlugwiseException as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="error_communicating_with_api",
                translation_placeholders={
                    "error": str(err),
                },
            ) from err
        finally:
            await self.coordinator.async_request_refresh()

    return handler
