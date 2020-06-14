"""Config flow for Plugwise Anna integration."""
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import exceptions
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import callback
from Plugwise_Smile.Smile import Smile

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PASSWORD): str,
    }, extra=vol.ALLOW_EXTRA
)

async def validate_input(hass: core.HomeAssistant, data):
    """
    Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(
        host=data["host"], password=data["password"], timeout=30, websession=websession
    )

    try:
        await api.connect()
    except Smile.InvalidAuthentication:
        raise InvalidAuth
    except Smile.PlugwiseError:
        raise CannotConnect

    return api


class PlugwiseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise Smile."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:

            try:
                api = await validate_input(self.hass, user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(api.gateway_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=api.smile_name, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors or {}
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

    async def async_step_init(self, user_input=None):
        """Manage the Plugwise options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        api = self.hass.data[DOMAIN][self.config_entry.entry_id]["api"]
        if api.smile_type == "power":
            SCAN_INTERVAL = DEFAULT_SCAN_INTERVAL["power"]
        else:
            SCAN_INTERVAL = DEFAULT_SCAN_INTERVAL["thermostat"]

        data = {
            vol.Optional(
                CONF_SCAN_INTERVAL, 
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, SCAN_INTERVAL
                )
            ): int
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(data))


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""