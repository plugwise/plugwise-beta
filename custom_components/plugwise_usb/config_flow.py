"""Config flow for Plugwise USB integration."""
from __future__ import annotations

from typing import Any

import serial.tools.list_ports  # pw-beta usb
import voluptuous as vol

from homeassistant.components import usb  # pw-beta usb
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_BASE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from plugwise_usb import Stick  # pw-beta usb

# pw-beta Note; the below are explicit through isort
from plugwise_usb.exceptions import NetworkDown  # pw-beta usb
from plugwise_usb.exceptions import PortError  # pw-beta usb
from plugwise_usb.exceptions import StickInitError  # pw-beta usb
from plugwise_usb.exceptions import TimeoutException  # pw-beta usb

# pw-beta Note; the below are explicit through isort
from .const import CONF_MANUAL_PATH  # pw-beta usb
from .const import CONF_USB_PATH  # pw-beta usb
from .const import DOMAIN


@callback
def plugwise_stick_entries(hass):  # pw-beta usb
    """Return existing connections for Plugwise USB-stick domain."""
    sticks = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        sticks.append(entry.data.get(CONF_USB_PATH))
    return sticks


# Github issue: #265
# Might be a `tuple[dict[str, str], Stick | None]` for typing, but that throws
# Item None of Optional[Any] not having attribute mac [union-attr]
async def validate_usb_connection(
    self, device_path=None
) -> tuple[dict[str, str], Any]:  # pw-beta usb
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


class PlugwiseUSBConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plugwise USB."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:  # pw-beta usb
        """Step when user initializes a integration."""
        errors: dict[str, str] = {}
        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        list_of_ports = [
            f"{p}, s/n: {p.serial_number or 'n/a'}"
            + (f" - {p.manufacturer}" if p.manufacturer else "")
            for p in ports
        ]
        list_of_ports.append(CONF_MANUAL_PATH)

        if user_input is not None:
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
                    title="Stick", data={CONF_USB_PATH: device_path}
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_USB_PATH): vol.In(list_of_ports)}
            ),
            errors=errors,
        )

    async def async_step_manual_path(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:  # pw-beta usb
        """Step when manual path to device."""
        errors: dict[str, str] = {}
        if user_input is not None:
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
