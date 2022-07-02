"""Test the Plugwise config flow."""
from unittest.mock import AsyncMock, MagicMock, patch

from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidSetupError,
    InvalidXMLError,
    NetworkDown,
    PlugwiseException,
    ResponseError,
    StickInitError,
    TimeoutException,
)
import pytest
import serial.tools.list_ports

from homeassistant.components.plugwise.config_flow import CONF_MANUAL_PATH
from homeassistant.components import zeroconf
from homeassistant.components.plugwise.const import (
    API,
    CONF_HOMEKIT_EMULATION,
    CONF_REFRESH_INTERVAL,
    CONF_USB_PATH,
    DEFAULT_PORT,
    DOMAIN,
    FLOW_NET,
    FLOW_TYPE,
    FLOW_USB,
    PW_TYPE,
    STICK,
)
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant

from homeassistant.data_entry_flow import (
    RESULT_TYPE_ABORT,
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
)
from tests.common import MockConfigEntry
from voluptuous.error import MultipleInvalid


TEST_HOST = "1.1.1.1"
TEST_HOSTNAME = "smileabcdef"
TEST_HOSTNAME2 = "stretchabc"
TEST_PASSWORD = "test_password"
TEST_PORT = 81
TEST_USBPORT = "/dev/ttyUSB1"
TEST_USBPORT2 = "/dev/ttyUSB2"
TEST_USERNAME = "smile"
TEST_USERNAME2 = "stretch"

TEST_DISCOVERY = zeroconf.ZeroconfServiceInfo(
    host=TEST_HOST,
    addresses=[TEST_HOST],
    hostname=f"{TEST_HOSTNAME}.local.",
    name="mock_name",
    port=DEFAULT_PORT,
    properties={
        "product": "smile",
        "version": "1.2.3",
        "hostname": f"{TEST_HOSTNAME}.local.",
    },
    type="mock_type",
)
TEST_DISCOVERY2 = zeroconf.ZeroconfServiceInfo(
    host=TEST_HOST,
    addresses=[TEST_HOST],
    hostname=f"{TEST_HOSTNAME2}.local.",
    name="mock_name",
    port=DEFAULT_PORT,
    properties={
        "product": "stretch",
        "version": "1.2.3",
        "hostname": f"{TEST_HOSTNAME2}.local.",
    },
    type="mock_type",
)


@pytest.fixture(name="mock_smile")
def mock_smile():
    """Create a Mock Smile for testing exceptions."""
    with patch(
        "homeassistant.components.plugwise.config_flow.Smile",
    ) as smile_mock:
        smile_mock.PlugwiseException = PlugwiseException
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.return_value.connect.return_value = True
        yield smile_mock.return_value


def com_port():
    """Mock of a serial port."""
    port = serial.tools.list_ports_common.ListPortInfo(TEST_USBPORT)
    port.serial_number = "1234"
    port.manufacturer = "Virtual serial port"
    port.device = TEST_USBPORT
    port.description = "Some serial port"
    return port


async def test_form_flow_gateway(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test we get the form for Plugwise Gateway product type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={FLOW_TYPE: FLOW_NET}
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user_gateway"


async def test_form_flow_usb(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test we get the form for Plugwise USB product type."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={FLOW_TYPE: FLOW_USB}
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user_usb"


async def test_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test the full user configuration flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user_gateway"
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: TEST_HOST,
            CONF_PASSWORD: TEST_PASSWORD,
        },
    )
    await hass.async_block_till_done()

    assert result2.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME,
        PW_TYPE: API,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 1


@pytest.mark.parametrize(
    "discovery,username",
    [
        (TEST_DISCOVERY, TEST_USERNAME),
        (TEST_DISCOVERY2, TEST_USERNAME2),
    ],
)
async def test_zeroconf_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
    discovery: ZeroconfServiceInfo,
    username: str,
) -> None:
    """Test config flow for Smile devices."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY,
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user_gateway"
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: TEST_PASSWORD},
    )
    await hass.async_block_till_done()

    assert result2.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME,
        PW_TYPE: API,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 1


async def test_zeroconf_stretch_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test config flow for Stretch devices."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY2,
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user_gateway"
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: TEST_PASSWORD},
    )
    await hass.async_block_till_done()

    assert result2.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME2,
        PW_TYPE: API,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 1


async def test_zercoconf_discovery_update_configuration(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test if a discovered device is configured and updated with new host."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CONF_NAME,
        data={
            CONF_HOST: "0.0.0.0",
            CONF_USERNAME: TEST_USERNAME,
            CONF_PASSWORD: TEST_PASSWORD,
        },
        unique_id=TEST_HOSTNAME,
    )
    entry.add_to_hass(hass)

    assert entry.data[CONF_HOST] == "0.0.0.0"

    # Test that an invalid discovery doesn't update the entry
    mock_smile_config_flow.connect.side_effect = ConnectionFailedError
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY,
    )
    assert result.get("type") == RESULT_TYPE_ABORT
    assert result.get("reason") == "already_configured"
    assert entry.data[CONF_HOST] == "0.0.0.0"

    mock_smile_config_flow.connect.side_effect = None
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY,
    )

    assert result.get("type") == RESULT_TYPE_ABORT
    assert result.get("reason") == "already_configured"
    assert entry.data[CONF_HOST] == "1.1.1.1"


@pytest.mark.parametrize(
    "side_effect,reason",
    [
        (InvalidSetupError, "invalid_setup"),
        (InvalidAuthentication, "invalid_auth"),
        (ConnectionFailedError, "cannot_connect"),
        (InvalidXMLError, "cannot_connect"),
        (ResponseError, "cannot_connect"),
        (RuntimeError, "unknown"),
    ],
)
async def test_flow_errors(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
    side_effect: Exception,
    reason: str,
) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    mock_smile_config_flow.connect.side_effect = side_effect
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={FLOW_TYPE: FLOW_NET}
    )
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result3.get("type") == RESULT_TYPE_FORM
    assert result3.get("errors") == {"base": reason}
    assert result3.get("step_id") == "user_gateway"

    assert len(mock_setup_entry.mock_calls) == 0
    assert len(mock_smile_config_flow.connect.mock_calls) == 1

    mock_smile_config_flow.connect.side_effect = None
    result4 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result4.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result4.get("title") == "Test Smile Name"
    assert result4.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME,
        PW_TYPE: API,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 2


async def test_form_invalid_setup(hass, mock_smile):
    """Test we handle invalid setup."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )

    mock_smile.connect.side_effect = InvalidSetupError
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_setup"}


async def test_form_invalid_auth(hass, mock_smile):
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )

    mock_smile.connect.side_effect = InvalidAuthentication
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass, mock_smile):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )

    mock_smile.connect.side_effect = ConnectionFailedError
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_cannot_connect_port(hass, mock_smile):
    """Test we handle cannot connect to port error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )

    mock_smile.connect.side_effect = ConnectionFailedError
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: TEST_HOST,
            CONF_PASSWORD: TEST_PASSWORD,
            CONF_PORT: TEST_PORT,
        },
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_other_problem(hass, mock_smile):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_NET}
    )

    mock_smile.connect.side_effect = TimeoutError
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "unknown"}


async def test_options_flow_thermo(hass, mock_smile_anna_2) -> None:
    """Test config flow options for thermostatic environments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CONF_NAME,
        data={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
        options={
            CONF_HOMEKIT_EMULATION: False,
            CONF_REFRESH_INTERVAL: 1.5,
            CONF_SCAN_INTERVAL: 60,
        },
    )

    hass.data[DOMAIN] = {
        entry.entry_id: {"coordinator": MagicMock(api=mock_smile_anna_2)}
    }
    entry.add_to_hass(hass)
    with patch(
        "homeassistant.components.plugwise.async_setup_entry", return_value=True
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] == RESULT_TYPE_FORM
        assert result["step_id"] == "init"

        assert result["type"] == RESULT_TYPE_CREATE_ENTRY
        assert result["data"] == {
            CONF_HOMEKIT_EMULATION: False,
            CONF_REFRESH_INTERVAL: 1.5,
            CONF_SCAN_INTERVAL: 60,
        }


@patch("serial.tools.list_ports.comports", MagicMock(return_value=[com_port()]))
@patch("plugwise.Stick.connect", MagicMock(return_value=None))
@patch("plugwise.Stick.initialize_stick", MagicMock(return_value=None))
@patch("plugwise.Stick.disconnect", MagicMock(return_value=None))
async def test_user_flow_select(hass):
    """Test user flow when USB-stick is selected from list."""
    port = com_port()
    port_select = f"{port}, s/n: {port.serial_number} - {port.manufacturer}"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_USB_PATH: port_select}
    )
    assert result["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {PW_TYPE: STICK, CONF_USB_PATH: TEST_USBPORT}

    # Retry to ensure configuring the same port is not allowed
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_USB_PATH: port_select}
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] == {"base": "already_configured"}


async def test_user_flow_manual_selected_show_form(hass):
    """Test user step form when manual path is selected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )
    assert result["type"] == RESULT_TYPE_FORM
    assert result["step_id"] == "manual_path"


async def test_user_flow_manual(hass):
    """Test user flow when USB-stick is manually entered."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )

    with patch(
        "homeassistant.components.plugwise.config_flow.Stick",
    ) as usb_mock:
        usb_mock.return_value.connect = MagicMock(return_value=True)
        usb_mock.return_value.initialize_stick = MagicMock(return_value=True)
        usb_mock.return_value.disconnect = MagicMock(return_value=True)
        usb_mock.return_value.mac = "01:23:45:67:AB"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_USB_PATH: TEST_USBPORT2},
        )
    assert result["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {CONF_USB_PATH: TEST_USBPORT2}


async def test_invalid_connection(hass):
    """Test invalid connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_USB_PATH: CONF_MANUAL_PATH},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_USB_PATH: "/dev/null"},
    )

    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_empty_connection(hass):
    """Test empty connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}, data={FLOW_TYPE: FLOW_USB}
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
        assert False
    except MultipleInvalid:
        assert True

    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] == {}


@patch("plugwise.Stick.connect", MagicMock(return_value=None))
@patch("plugwise.Stick.initialize_stick", MagicMock(side_effect=(StickInitError)))
async def test_failed_initialization(hass):
    """Test we handle failed initialization of Plugwise USB-stick."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
        data={FLOW_TYPE: FLOW_USB},
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


@patch("plugwise.Stick.connect", MagicMock(return_value=None))
@patch("plugwise.Stick.initialize_stick", MagicMock(side_effect=(NetworkDown)))
async def test_network_down_exception(hass):
    """Test we handle network_down exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
        data={FLOW_TYPE: FLOW_USB},
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


@patch("plugwise.Stick.connect", MagicMock(return_value=None))
@patch("plugwise.Stick.initialize_stick", MagicMock(side_effect=(TimeoutException)))
async def test_timeout_exception(hass):
    """Test we handle time exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
        data={FLOW_TYPE: FLOW_USB},
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


async def test_options_flow_stick(hass) -> None:
    """Test config flow options lack for stick environments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CONF_NAME,
        data={FLOW_TYPE: FLOW_USB},
    )
    hass.data[DOMAIN] = {entry.entry_id: {"api_stick": MagicMock()}}
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.plugwise.async_setup_entry", return_value=True
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)

        assert result["type"] == RESULT_TYPE_FORM
        assert result["step_id"] == "none"


async def test_options_flow_stick_with_input(hass) -> None:
    """Test config flow options lack for stick environments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CONF_NAME,
        data={FLOW_TYPE: FLOW_USB},
    )
    hass.data[DOMAIN] = {entry.entry_id: {"api_stick": MagicMock()}}
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.plugwise.async_setup_entry", return_value=True
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_USB_PATH: TEST_USBPORT2},
        )

        assert result["type"] == RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == ""
