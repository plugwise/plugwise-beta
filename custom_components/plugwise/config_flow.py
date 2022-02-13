"""Config flow for Plugwise integration."""
from __future__ import annotations

from typing import Any

from plugwise.exceptions import (
    InvalidAuthentication,
    NetworkDown,
    PlugwiseException,
    PortError,
    StickInitError,
    TimeoutException,
)
from plugwise.smile import Smile
from plugwise.stick import Stick
import serial.tools.list_ports
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.components import usb
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_BASE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import callback, HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API,
    CONF_USB_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    FLOW_NET,
    FLOW_SMILE,
    FLOW_STRETCH,
    FLOW_TYPE,
    FLOW_USB,
    LOGGER,
    PW_TYPE,
    SMILE,
    STICK,
    STRETCH,
    STRETCH_USERNAME,
    ZEROCONF_MAP,
)


CONF_MANUAL_PATH = "Enter Manually"

CONNECTION_SCHEMA = vol.Schema(
    {vol.Required(FLOW_TYPE, default=FLOW_NET): vol.In([FLOW_NET, FLOW_USB])}
)


@callback
def plugwise_stick_entries(hass):
    """Return existing connections for Plugwise USB-stick domain."""
    sticks = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(PW_TYPE) == STICK:
            sticks.append(entry.data.get(CONF_USB_PATH))
    return sticks


async def validate_usb_connection(self, device_path=None) -> dict[str, str]:
    """Test if device_path is a real Plugwise USB-Stick."""
    errors = {}

    # Avoid creating a 2nd connection to an already configured stick
    if device_path in plugwise_stick_entries(self):
        errors[CONF_BASE] = "already_configured"
        return errors, None

    api_stick = await self.async_add_executor_job(Stick, device_path)
    try:
        await self.async_add_executor_job(api_stick.connect)
        await self.async_add_executor_job(api_stick.initialize_stick)
        await self.async_add_executor_job(api_stick.disconnect)
    except PortError:
        errors[CONF_BASE] = "cannot_connect"
    except StickInitError:
        errors[CONF_BASE] = "stick_init"
    except NetworkDown:
        errors[CONF_BASE] = "network_down"
    except TimeoutException:
        errors[CONF_BASE] = "network_timeout"
    return errors, api_stick


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


async def validate_gw_input(hass: HomeAssistant, data: dict[str, Any]) -> Smile:
    """
    Validate whether the user input allows us to connect to the gateway.

    Data has the keys from _base_gw_schema() with values provided by the user.
    """
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Smile(
        host=data[CONF_HOST],
        password=data[CONF_PASSWORD],
        port=data[CONF_PORT],
        username=data[CONF_USERNAME],
        timeout=30,
        websession=websession,
    )
    await api.connect()
    return api


class PlugwiseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise Smile."""

    VERSION = 1

    discovery_info: ZeroconfServiceInfo | None = None
    _username: str = DEFAULT_USERNAME

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Prepare configuration for a discovered Plugwise Smile."""
        self.discovery_info = discovery_info
        _properties = discovery_info.properties

        unique_id = discovery_info.hostname.split(".")[0]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured({CONF_HOST: discovery_info.host})

        if DEFAULT_USERNAME not in unique_id:
            self._username = STRETCH_USERNAME
        _product = _properties.get("product", None)
        _version = _properties.get("version", "n/a")
        _name = f"{ZEROCONF_MAP.get(_product, _product)} v{_version}"

        self.context.update(
            {
                "title_placeholders": {
                    CONF_HOST: discovery_info.host,
                    CONF_NAME: _name,
                    CONF_PORT: discovery_info.port,
                    CONF_USERNAME: self._username,
                },
                "configuration_url": f"http://{discovery_info.host}:{discovery_info.port}",
            }
        )
        return await self.async_step_user_gateway()

    async def async_step_user_usb(self, user_input=None):
        """Step when user initializes a integration."""
        errors = {}
        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = [
            f"{p}, s/n: {p.serial_number or 'n/a'}"
            + (f" - {p.manufacturer}" if p.manufacturer else "")
            for p in ports
        ]
        list_of_ports.append(CONF_MANUAL_PATH)

        if user_input is not None:
            user_input.pop(FLOW_TYPE, None)
            user_selection = user_input[CONF_USB_PATH]

            if user_selection == CONF_MANUAL_PATH:
                return await self.async_step_manual_path()

            port = ports[list_of_ports.index(user_selection)]
            device_path = await self.hass.async_add_executor_job(
                usb.get_serial_by_id, port.device
            )
            errors, api_stick = await validate_usb_connection(self.hass, device_path)
            if not errors:
                await self.async_set_unique_id(api_stick.mac)
                return self.async_create_entry(
                    title="Stick", data={CONF_USB_PATH: device_path, PW_TYPE: STICK}
                )
        return self.async_show_form(
            step_id="user_usb",
            data_schema=vol.Schema(
                {vol.Required(CONF_USB_PATH): vol.In(list_of_ports)}
            ),
            errors=errors,
        )

    async def async_step_manual_path(self, user_input=None):
        """Step when manual path to device."""
        errors = {}
        if user_input is not None:
            user_input.pop(FLOW_TYPE, None)
            device_path = await self.hass.async_add_executor_job(
                usb.get_serial_by_id, user_input.get(CONF_USB_PATH)
            )
            errors, api_stick = await validate_usb_connection(self.hass, device_path)
            if not errors:
                await self.async_set_unique_id(api_stick.mac)
                return self.async_create_entry(
                    title="Stick", data={CONF_USB_PATH: device_path}
                )
        return self.async_show_form(
            step_id="manual_path",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USB_PATH, default="/dev/ttyUSB0" or vol.UNDEFINED
                    ): str
                }
            ),
            errors=errors,
        )

    async def async_step_user_gateway(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step when using network/gateway setups."""
        errors = {}

        if user_input is not None:
            if self.discovery_info:
                user_input[CONF_HOST] = self.discovery_info.host
                user_input[CONF_PORT] = self.discovery_info.port
                user_input[CONF_USERNAME] = self._username

            try:
                api = await validate_gw_input(self.hass, user_input)
            except InvalidAuthentication:
                errors[CONF_BASE] = "invalid_auth"
            except PlugwiseException:
                errors[CONF_BASE] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors[CONF_BASE] = "unknown"
            else:
                await self.async_set_unique_id(
                    api.smile_hostname or api.gateway_id, raise_on_progress=False
                )
                self._abort_if_unique_id_configured()

                user_input[PW_TYPE] = API
                return self.async_create_entry(title=api.smile_name, data=user_input)

        return self.async_show_form(
            step_id="user",
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

    async def async_step_none(self, user_input=None):
        """No options available."""
        if user_input is not None:
            # Apparently not possible to abort an options flow at the moment
            return self.async_create_entry(title="", data=self.config_entry.options)

        return self.async_show_form(step_id="none")

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
