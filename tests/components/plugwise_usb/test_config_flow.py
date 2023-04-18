"""Test the Plugwise config flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import serial.tools.list_ports
from voluptuous.error import MultipleInvalid

from homeassistant.components.plugwise_usb.config_flow import CONF_MANUAL_PATH
from homeassistant.components.plugwise_usb.const import CONF_USB_PATH, DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_SOURCE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from plugwise_usb.exceptions import NetworkDown, StickInitError, TimeoutException

TEST_USBPORT = "/dev/ttyUSB1"
TEST_USBPORT2 = "/dev/ttyUSB2"


def com_port():
    """Mock of a serial port."""
    port = serial.tools.list_ports_common.ListPortInfo(TEST_USBPORT)
    port.serial_number = "1234"
    port.manufacturer = "Virtual serial port"
    port.device = TEST_USBPORT
    port.description = "Some serial port"
    return port


async def test_form_flow_usb(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test we get the form for Plugwise USB product type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"


@patch("serial.tools.list_ports.comports", MagicMock(return_value=[com_port()]))
@patch("plugwise_usb.Stick.connect", MagicMock(return_value=None))
@patch("plugwise_usb.Stick.initialize_stick", MagicMock(return_value=None))
@patch("plugwise_usb.Stick.disconnect", MagicMock(return_value=None))
async def test_user_flow_select(hass):
    """Test user flow when USB-stick is selected from list."""
    port = com_port()
    port_select = f"{port}, s/n: {port.serial_number} - {port.manufacturer}"

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_USB_PATH: port_select}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_USB_PATH: TEST_USBPORT}

    # Retry to ensure configuring the same port is not allowed
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_USB_PATH: port_select}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "already_configured"}


async def test_user_flow_manual_selected_show_form(hass):
    """Test user step form when manual path is selected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "manual_path"


async def test_user_flow_manual(hass):
    """Test user flow when USB-stick is manually entered."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )

    with patch(
        "homeassistant.components.plugwise_usb.config_flow.Stick",
    ) as usb_mock:
        usb_mock.return_value.connect = MagicMock(return_value=True)
        usb_mock.return_value.initialize_stick = MagicMock(return_value=True)
        usb_mock.return_value.disconnect = MagicMock(return_value=True)
        usb_mock.return_value.mac = "01:23:45:67:AB"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_USB_PATH: TEST_USBPORT2},
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_USB_PATH: TEST_USBPORT2}


async def test_invalid_connection(hass):
    """Test invalid connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USB_PATH: "/dev/null"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_empty_connection(hass):
    """Test empty connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )

    try:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USB_PATH: None},
        )
        pytest.fail("Empty connection was accepted")
    except MultipleInvalid:
        assert True

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}


@patch("plugwise_usb.Stick.connect", MagicMock(return_value=None))
@patch("plugwise_usb.Stick.initialize_stick", MagicMock(side_effect=(StickInitError)))
async def test_failed_initialization(hass):
    """Test we handle failed initialization of Plugwise USB-stick."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: "/dev/null"},
    )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "stick_init"}


@patch("plugwise_usb.Stick.connect", MagicMock(return_value=None))
@patch("plugwise_usb.Stick.initialize_stick", MagicMock(side_effect=(NetworkDown)))
async def test_network_down_exception(hass):
    """Test we handle network_down exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: "/dev/null"},
    )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "network_down"}


@patch("plugwise_usb.Stick.connect", MagicMock(return_value=None))
@patch("plugwise_usb.Stick.initialize_stick", MagicMock(side_effect=(TimeoutException)))
async def test_timeout_exception(hass):
    """Test we handle time exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: "/dev/null"},
    )
    assert result["type"] == "form"
    assert result["errors"] == {"base": "network_timeout"}
