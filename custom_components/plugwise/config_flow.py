"""Config flow for Plugwise integration."""

from __future__ import annotations

import datetime as dt  # pw-beta options
from typing import Any

from plugwise import Smile
from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidSetupError,
    InvalidXMLError,
    ResponseError,
    UnsupportedDeviceError,
)
import voluptuous as vol

from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import (
    SOURCE_USER,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithConfigEntry,
)

# Upstream
from homeassistant.const import (
    ATTR_CONFIGURATION_URL,
    CONF_BASE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)

# Upstream
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from packaging import version

from .const import (
    ANNA_WITH_ADAM,
    CONF_HOMEKIT_EMULATION,  # pw-beta option
    CONF_REFRESH_INTERVAL,  # pw-beta option
    CONF_VERSION,
    CONTEXT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,  # pw-beta option
    DEFAULT_TIMEOUT,
    DEFAULT_USERNAME,
    DOMAIN,
    FLOW_ID,
    FLOW_SMILE,
    FLOW_STRETCH,
    INIT,
    PRODUCT,
    SMILE,
    SMILE_OPEN_THERM,
    SMILE_THERMO,
    STRETCH,
    STRETCH_USERNAME,
    THERMOSTAT,
    TITLE_PLACEHOLDERS,
    VERSION,
    ZEROCONF_MAP,
)

# Upstream
from .coordinator import PlugwiseDataUpdateCoordinator

type PlugwiseConfigEntry = ConfigEntry[PlugwiseDataUpdateCoordinator]

# Upstream basically the whole file (excluding the pw-beta options)


def _base_schema(
    discovery_info: ZeroconfServiceInfo | None,
    user_input: dict[str, Any] | None,
) -> vol.Schema:
    """Generate base schema for gateways."""
    if not discovery_info:
        if not user_input:
            return vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_USERNAME, default=SMILE): vol.In(
                        {SMILE: FLOW_SMILE, STRETCH: FLOW_STRETCH}
                    ),
                }
            )
        return vol.Schema(
            {
                vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                vol.Optional(CONF_PORT, default=user_input[CONF_PORT]): int,
                vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): vol.In(
                    {SMILE: FLOW_SMILE, STRETCH: FLOW_STRETCH}
                ),
            }
        )
    return vol.Schema({vol.Required(CONF_PASSWORD): str})


def get_timeout_for_version(version_str: str) -> int:
    """Determine timeout value based on gateway version."""
    if version.parse(version_str) >= version.parse("3.2.0"):
        return 10
    return DEFAULT_TIMEOUT


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> Smile:
    """Validate whether the user input allows us to connect to the gateway.

    Data has the keys from _base_schema() with values provided by the user.
    """
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(
        host=data[CONF_HOST],
        password=data[CONF_PASSWORD],
        port=data[CONF_PORT],
        username=data[CONF_USERNAME],
        timeout=data[CONF_TIMEOUT],
        websession=websession,
    )
    await api.connect()
    return api


class PlugwiseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise Smile."""

    VERSION = 1
    MINOR_VERSION = 2

    discovery_info: ZeroconfServiceInfo | None = None
    _username: str = DEFAULT_USERNAME
    _timeout: int = DEFAULT_TIMEOUT

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Prepare configuration for a discovered Plugwise Smile."""
        self.discovery_info = discovery_info
        _properties = discovery_info.properties

        unique_id = discovery_info.hostname.split(".")[0].split("-")[0]
        if config_entry := await self.async_set_unique_id(unique_id):
            try:
                await validate_input(
                    self.hass,
                    {
                        CONF_HOST: discovery_info.host,
                        CONF_PASSWORD: config_entry.data[CONF_PASSWORD],
                        CONF_PORT: discovery_info.port,
                        CONF_USERNAME: config_entry.data[CONF_USERNAME],
                        CONF_TIMEOUT: self._timeout,
                    },
                )
            except Exception:  # noqa: BLE001
                self._abort_if_unique_id_configured()
            else:
                self._abort_if_unique_id_configured(
                    {
                        CONF_HOST: discovery_info.host,
                        CONF_PORT: discovery_info.port,
                    }
                )

        if DEFAULT_USERNAME not in unique_id:
            self._username = STRETCH_USERNAME
        _product = _properties.get(PRODUCT, None)
        _version = _properties.get(VERSION, "n/a")
        _name = f"{ZEROCONF_MAP.get(_product, _product)} v{_version}"

        self._timeout = get_timeout_for_version(_version)

        # This is an Anna, but we already have config entries.
        # Assuming that the user has already configured Adam, aborting discovery.
        if self._async_current_entries() and _product == SMILE_THERMO:
            return self.async_abort(reason=ANNA_WITH_ADAM)

        # If we have discovered an Adam or Anna, both might be on the network.
        # In that case, we need to cancel the Anna flow, as the Adam should
        # be added.
        for flow in self._async_in_progress():
            # This is an Anna, and there is already an Adam flow in progress
            if (
                _product == SMILE_THERMO
                and CONTEXT in flow
                and flow[CONTEXT].get(PRODUCT) == SMILE_OPEN_THERM
            ):
                return self.async_abort(reason=ANNA_WITH_ADAM)

            # This is an Adam, and there is already an Anna flow in progress
            if (
                _product == SMILE_OPEN_THERM
                and CONTEXT in flow
                and flow[CONTEXT].get(PRODUCT) == SMILE_THERMO
                and FLOW_ID in flow
            ):
                self.hass.config_entries.flow.async_abort(flow[FLOW_ID])

        self.context.update(
            {
                TITLE_PLACEHOLDERS: {
                    CONF_HOST: discovery_info.host,
                    CONF_NAME: _name,
                    CONF_PORT: discovery_info.port,
                    CONF_TIMEOUT: self._timeout,
                    CONF_USERNAME: self._username,
                    CONF_VERSION: _version,
                },
                ATTR_CONFIGURATION_URL: (
                    f"http://{discovery_info.host}:{discovery_info.port}"
                ),
                PRODUCT: _product,
            }
        )
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step when using network/gateway setups."""
        errors: dict[str, str] = {}

        if not user_input:
            return self.async_show_form(
                step_id=SOURCE_USER,
                data_schema=_base_schema(self.discovery_info, None),
                errors=errors,
            )

        if self.discovery_info:
            user_input[CONF_HOST] = self.discovery_info.host
            user_input[CONF_PORT] = self.discovery_info.port
            user_input[CONF_USERNAME] = self._username

        user_input[CONF_TIMEOUT] = self._timeout
        try:
            api = await validate_input(self.hass, user_input)
        except ConnectionFailedError:
            errors[CONF_BASE] = "cannot_connect"
        except InvalidAuthentication:
            errors[CONF_BASE] = "invalid_auth"
        except InvalidSetupError:
            errors[CONF_BASE] = "invalid_setup"
        except (InvalidXMLError, ResponseError):
            errors[CONF_BASE] = "response_error"
        except UnsupportedDeviceError:
            errors[CONF_BASE] = "unsupported"
        except Exception:  # noqa: BLE001
            errors[CONF_BASE] = "unknown"

        if errors:
            return self.async_show_form(
                step_id=SOURCE_USER,
                data_schema=_base_schema(None, user_input),
                errors=errors,
            )

        user_input[CONF_VERSION] = api.smile_version

        await self.async_set_unique_id(
            api.smile_hostname or api.gateway_id, raise_on_progress=False
        )
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=api.smile_name, data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: PlugwiseConfigEntry,
    ) -> OptionsFlow:  # pw-beta options
        """Get the options flow for this handler."""
        return PlugwiseOptionsFlowHandler(config_entry)


# pw-beta - change the scan-interval via CONFIGURE
# pw-beta - add homekit emulation via CONFIGURE
# pw-beta - change the frontend refresh interval via CONFIGURE
class PlugwiseOptionsFlowHandler(OptionsFlowWithConfigEntry):  # pw-beta options
    """Plugwise option flow."""

    async def async_step_none(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:  # pragma: no cover
        """No options available."""
        if user_input is not None:
            # Apparently not possible to abort an options flow at the moment
            return self.async_create_entry(title="", data=self._options)
        return self.async_show_form(step_id="none")

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:  # pragma: no cover
        """Manage the Plugwise options."""
        if not self.config_entry.data.get(CONF_HOST):
            return await self.async_step_none(user_input)

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        coordinator = self.config_entry.runtime_data
        interval: dt.timedelta = DEFAULT_SCAN_INTERVAL[
            coordinator.api.smile_type
        ]  # pw-beta options

        data = {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self._options.get(
                    CONF_SCAN_INTERVAL, interval.seconds
                ),
            ): vol.All(cv.positive_int, vol.Clamp(min=10)),
        }  # pw-beta

        if coordinator.api.smile_type != THERMOSTAT:
            return self.async_show_form(step_id=INIT, data_schema=vol.Schema(data))

        data.update(
            {
                vol.Optional(
                    CONF_HOMEKIT_EMULATION,
                    default=self._options.get(
                        CONF_HOMEKIT_EMULATION, False
                    ),
                ): vol.All(cv.boolean),
                vol.Optional(
                    CONF_REFRESH_INTERVAL,
                    default=self._options.get(CONF_REFRESH_INTERVAL, 1.5),
                ): vol.All(vol.Coerce(float), vol.Range(min=1.5, max=10.0)),
            }
        )  # pw-beta
        return self.async_show_form(step_id=INIT, data_schema=vol.Schema(data))
