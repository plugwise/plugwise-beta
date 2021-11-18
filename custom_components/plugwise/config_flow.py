"""Config flow for Plugwise integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.const import (
    CONF_BASE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import DiscoveryInfoType

from plugwise.exceptions import (
    InvalidAuthentication,
    PlugwiseException,
)
from plugwise.smile import Smile

from .const import (
    API,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    FLOW_NET,
    FLOW_SMILE,
    FLOW_STRETCH,
    FLOW_TYPE,
    FLOW_USB,
    PW_TYPE,
    SMILE,
    STRETCH,
    STRETCH_USERNAME,
    ZEROCONF_MAP,
)

_LOGGER = logging.getLogger(__name__)

CONF_MANUAL_PATH = "Enter Manually"

CONNECTION_SCHEMA = vol.Schema(
    {vol.Required(FLOW_TYPE, default=FLOW_NET): vol.In([FLOW_NET, FLOW_USB])}
)


# PLACEHOLDER USB connection validation

def _base_gw_schema(discovery_info):
    """Generate base schema for gateways."""
    base_gw_schema = {}

    if not discovery_info:
        base_gw_schema[vol.Required(CONF_HOST)] = str
        base_gw_schema[vol.Optional(CONF_PORT, default=DEFAULT_PORT)] = int
        base_gw_schema[vol.Required(CONF_USERNAME, default=SMILE)] = vol.In(
            {SMILE: FLOW_SMILE, STRETCH: FLOW_STRETCH}
        )

    base_gw_schema.update({vol.Required(CONF_PASSWORD): str})

    return vol.Schema(base_gw_schema)


async def validate_gw_input(hass: core.HomeAssistant, data):
    """
    Validate whether the user input allows us to connect to the gateway.

    Data has the keys from _base_gw_schema() with values provided by the user.
    """
    websession = async_get_clientsession(hass, verify_ssl=False)

    api = Smile(
        host=data[CONF_HOST],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        port=data[CONF_PORT],
        timeout=30,
        websession=websession,
    )

    try:
        await api.connect()
    except InvalidAuthentication as err:
        raise InvalidAuth from err
    except PlugwiseException as err:
        raise CannotConnect from err

    return api


class PlugwiseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise Smile."""

    VERSION = 1

    def __init__(self):
        """Initialize the Plugwise config flow."""
        self.discovery_info = {}

    async def async_step_zeroconf(self, discovery_info: DiscoveryInfoType):
        """Prepare configuration for a discovered Plugwise Smile."""
        self.discovery_info = discovery_info
        self.discovery_info[CONF_USERNAME] = DEFAULT_USERNAME
        _LOGGER.debug("Discovery info: %s", self.discovery_info)
        _properties = self.discovery_info.get("properties")

        # unique_id is needed here, to be able to determine whether the discovered device is known, or not.
        unique_id = self.discovery_info.get("hostname").split(".")[0]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured({CONF_HOST: self.discovery_info[CONF_HOST]})

        if DEFAULT_USERNAME not in unique_id:
            self.discovery_info[CONF_USERNAME] = STRETCH_USERNAME
        _product = _properties.get("product", None)
        _version = _properties.get("version", "n/a")
        _name = f"{ZEROCONF_MAP.get(_product, _product)} v{_version}"

        # pylint: disable=no-member # https://github.com/PyCQA/pylint/issues/3167
        self.context["title_placeholders"] = {
            CONF_HOST: self.discovery_info[CONF_HOST],
            CONF_NAME: _name,
            CONF_PORT: self.discovery_info[CONF_PORT],
            CONF_USERNAME: self.discovery_info[CONF_USERNAME],
        }
        return await self.async_step_user_gateway()

# PLACEHOLDER USB step_user

    async def async_step_user_gateway(self, user_input=None):
        """Handle the initial step when using network/gateway setups."""
        api = None
        errors = {}

        if user_input is not None:
            user_input.pop(FLOW_TYPE, None)

            if self.discovery_info:
                user_input[CONF_HOST] = self.discovery_info[CONF_HOST]
                user_input[CONF_PORT] = self.discovery_info[CONF_PORT]
                user_input[CONF_USERNAME] = self.discovery_info[CONF_USERNAME]

            try:
                api = await validate_gw_input(self.hass, user_input)

            except CannotConnect:
                errors[CONF_BASE] = "cannot_connect"
            except InvalidAuth:
                errors[CONF_BASE] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors[CONF_BASE] = "unknown"

            if not errors:
                await self.async_set_unique_id(
                    api.smile_hostname or api.gateway_id, raise_on_progress=False
                )
                self._abort_if_unique_id_configured()

                user_input[PW_TYPE] = API
                return self.async_create_entry(title=api.smile_name, data=user_input)

        return self.async_show_form(
            step_id="user_gateway",
            data_schema=_base_gw_schema(self.discovery_info),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step when using network/gateway setups."""
        errors = {}
        if user_input is not None:
            if user_input[FLOW_TYPE] == FLOW_NET:
                return await self.async_step_user_gateway()

            if user_input[FLOW_TYPE] == FLOW_USB:
                return await self.async_step_user_usb()

        return self.async_show_form(
            step_id="user",
            data_schema=CONNECTION_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PlugwiseOptionsFlowHandler(config_entry)


class PlugwiseOptionsFlowHandler(config_entries.OptionsFlow):
    """Plugwise option flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    # PLACEHOLDER USB async_step_none

    async def async_step_init(self, user_input=None):
        """Manage the Plugwise options."""
        if not self.config_entry.data.get(CONF_HOST):
            return await self.async_step_none(user_input)

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        api = self.hass.data[DOMAIN][self.config_entry.entry_id][API]
        interval = DEFAULT_SCAN_INTERVAL[api.smile_type]

        data = {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, interval),
            ): int
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(data))


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
