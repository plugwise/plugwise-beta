"""Config flow for Plugwise integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import (
    CONF_BASE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.core import callback
from Plugwise_Smile.Smile import Smile

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

ZEROCONF_MAP = {
    "smile": "P1",
    "smile_thermo": "Anna",
    "smile_open_therm": "Adam",
    "stretch": "Stretch",
}


def _base_schema(discovery_info):
    """Generate base schema."""
    base_schema = {}

    if not discovery_info:
        base_schema[vol.Required(CONF_HOST)] = str
        base_schema[vol.Optional(CONF_PORT, default=DEFAULT_PORT)] = int

    base_schema.update(
        {
            vol.Required(CONF_USERNAME, description={"suggested_value": "smile"}): str,
            vol.Required(CONF_PASSWORD): str,
        }
    )

    return vol.Schema(base_schema)


async def validate_input(hass: core.HomeAssistant, data):
    """
    Validate whether the user input allows us to connect.

    Data has the keys from _base_schema() with values provided by the user.
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
    except Smile.InvalidAuthentication:
        raise InvalidAuth
    except Smile.PlugwiseError:
        raise CannotConnect

    return api


class PlugwiseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise Smile."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the Plugwise config flow."""
        self.discovery_info = {}

    async def async_step_zeroconf(self, discovery_info: DiscoveryInfoType):
        """Prepare configuration for a discovered Plugwise Smile."""
        self.discovery_info = discovery_info
        _LOGGER.debug("Discovery info: %s", self.discovery_info)
        _properties = self.discovery_info.get("properties")

        unique_id = self.discovery_info.get("hostname").split(".")[0]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        _product = _properties.get("product", None)
        _version = _properties.get("version", "n/a")
        _LOGGER.debug("Discovered: %s", _properties)
        _LOGGER.debug("Plugwise Smile discovered with %s", _properties)
        _name = f"{ZEROCONF_MAP.get(_product, _product)} v{_version}"

        # pylint: disable=no-member # https://github.com/PyCQA/pylint/issues/3167
        self.context["title_placeholders"] = {
            CONF_HOST: self.discovery_info[CONF_HOST],
            CONF_NAME: _name,
        }
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:

            if self.discovery_info:
                user_input[CONF_HOST] = self.discovery_info[CONF_HOST]

            for entry in self._async_current_entries():
                if entry.data.get(CONF_HOST) == user_input[CONF_HOST]:
                    return self.async_abort(reason="already_configured")

            try:
                api = await validate_input(self.hass, user_input)

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

                return self.async_create_entry(title=api.smile_name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(self.discovery_info),
            errors=errors or {},
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
