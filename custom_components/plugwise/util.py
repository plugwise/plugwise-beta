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
# R = TypeVar("_R")
# P = ParamSpec("_P")


def plugwise_command[PlugwiseEntityT: PlugwiseEntity, **P, R](
    func: Callable[Concatenate[PlugwiseEntityT, P], Awaitable[R]],
) -> Callable[Concatenate[PlugwiseEntityT, P], Coroutine[Any, Any, R]]:
    """Decorate Plugwise calls that send commands/make changes to the device.

    A decorator that wraps the passed in function, catches Plugwise errors,
    and requests an coordinator update to update status of the devices asap.
    """

    async def handler(
        self: PlugwiseEntityT, *args: P.args, **kwargs: P.kwargs
    ) -> R:
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
