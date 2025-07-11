"""Test the Plugwise config flow."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidSetupError,
    InvalidXMLError,
    UnsupportedDeviceError,
)
import pytest

from homeassistant.components import zeroconf
from homeassistant.components.plugwise.const import (
    CONF_HOMEKIT_EMULATION,
    CONF_REFRESH_INTERVAL,
    DEFAULT_PORT,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER, SOURCE_ZEROCONF, ConfigFlowResult
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from packaging.version import Version

from tests.common import MockConfigEntry

TEST_HOST = "1.1.1.1"
TEST_HOSTNAME = "smileabcdef"
TEST_HOSTNAME2 = "stretchabc"
TEST_PASSWORD = "test_password"
TEST_PORT = 81
TEST_USERNAME = "smile"
TEST_USERNAME2 = "stretch"
TEST_SMILE_ID = "smile12345"

TEST_DISCOVERY = zeroconf.ZeroconfServiceInfo(
    ip_address=TEST_HOST,
    ip_addresses=[TEST_HOST],
    # The added `-2` is to simulate mDNS collision
    hostname=f"{TEST_HOSTNAME}-2.local.",
    name="mock_name",
    port=DEFAULT_PORT,
    properties={
        "product": "smile",
        "version": "4.1.2",
        "hostname": f"{TEST_HOSTNAME}.local.",
    },
    type="mock_type",
)
TEST_DISCOVERY2 = zeroconf.ZeroconfServiceInfo(
    ip_address=TEST_HOST,
    ip_addresses=[TEST_HOST],
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

TEST_DISCOVERY_ANNA = ZeroconfServiceInfo(
    ip_address=TEST_HOST,
    ip_addresses=[TEST_HOST],
    hostname=f"{TEST_HOSTNAME}.local.",
    name="mock_name",
    port=DEFAULT_PORT,
    properties={
        "product": "smile_thermo",
        "version": "3.2.1",
        "hostname": f"{TEST_HOSTNAME}.local.",
    },
    type="mock_type",
)

TEST_DISCOVERY_ADAM = ZeroconfServiceInfo(
    ip_address=TEST_HOST,
    ip_addresses=[TEST_HOST],
    hostname=f"{TEST_HOSTNAME2}.local.",
    name="mock_name",
    port=DEFAULT_PORT,
    properties={
        "product": "smile_open_therm",
        "version": "4.3.2",
        "hostname": f"{TEST_HOSTNAME2}.local.",
    },
    type="mock_type",
)


@pytest.fixture(name="mock_smile")
def mock_smile() -> Generator[MagicMock]:
    """Create a Mock Smile for testing exceptions."""
    with patch(
        "homeassistant.components.plugwise.config_flow.Smile",
    ) as smile_mock:
        smile_mock.ConnectionFailedError = ConnectionFailedError
        smile_mock.InvalidAuthentication = InvalidAuthentication
        smile_mock.InvalidXMLError = InvalidXMLError
        smile_mock.UnsupportedDeviceError = UnsupportedDeviceError
        smile_mock.return_value.connect.return_value = Version("4.3.2")
        yield smile_mock.return_value


async def test_form(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
) -> None:
    """Test the full user configuration flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={CONF_SOURCE: SOURCE_USER}
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: TEST_HOST,
            CONF_PASSWORD: TEST_PASSWORD,
        },
    )
    await hass.async_block_till_done()

    assert result2.get("type") == FlowResultType.CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 1


@pytest.mark.parametrize(
    ("discovery", "username",),
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
        data=discovery,
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: TEST_PASSWORD},
    )
    await hass.async_block_till_done()

    assert result2.get("type") == FlowResultType.CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: username,
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
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PASSWORD: TEST_PASSWORD},
    )
    await hass.async_block_till_done()

    assert result2.get("type") == FlowResultType.CREATE_ENTRY
    assert result2.get("title") == "Test Smile Name"
    assert result2.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME2,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 1


async def test_zeroconf_abort_anna_with_existing_config_entries(
    hass: HomeAssistant,
    mock_smile_adam: MagicMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test we abort Anna discovery with existing config entries."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY_ANNA,
    )
    assert result.get("type") == FlowResultType.ABORT
    assert result.get("reason") == "anna_with_adam"


async def test_zeroconf_abort_anna_with_adam(hass: HomeAssistant) -> None:
    """Test we abort Anna discovery when an Adam is also discovered."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY_ANNA,
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("step_id") == "user"

    flows_in_progress = hass.config_entries.flow._handler_progress_index[DOMAIN]
    assert len(flows_in_progress) == 1
    assert list(flows_in_progress)[0].product == "smile_thermo"

    # Discover Adam, Anna should be aborted and no longer present
    result2 = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY_ADAM,
    )

    assert result2.get("type") == FlowResultType.FORM
    assert result2.get("step_id") == "user"

    flows_in_progress = hass.config_entries.flow._handler_progress_index[DOMAIN]
    assert len(flows_in_progress) == 1
    assert list(flows_in_progress)[0].product == "smile_open_therm"

    # Discover Anna again, Anna should be aborted directly
    result3 = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY_ANNA,
    )
    assert result3.get("type") == FlowResultType.ABORT
    assert result3.get("reason") == "anna_with_adam"

    # Adam should still be there
    flows_in_progress = hass.config_entries.flow._handler_progress_index[DOMAIN]
    assert len(flows_in_progress) == 1
    assert list(flows_in_progress)[0].product == "smile_open_therm"


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
    assert result.get("type") == FlowResultType.ABORT
    assert result.get("reason") == "already_configured"
    assert entry.data[CONF_HOST] == "0.0.0.0"

    mock_smile_config_flow.connect.side_effect = None
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_ZEROCONF},
        data=TEST_DISCOVERY,
    )

    assert result.get("type") == FlowResultType.ABORT
    assert result.get("reason") == "already_configured"
    assert entry.data[CONF_HOST] == "1.1.1.1"


@pytest.mark.parametrize(
    ("side_effect", "reason"),
    [
        (ConnectionFailedError, "cannot_connect"),
        (InvalidAuthentication, "invalid_auth"),
        (InvalidSetupError, "invalid_setup"),
        (InvalidXMLError, "response_error"),
        (TimeoutError, "unknown"),
        (UnsupportedDeviceError, "unsupported"),
    ],
)
async def test_flow_errors(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_smile_config_flow: MagicMock,
    side_effect: Exception,
    reason: str,
) -> None:
    """Test various type of possible errorcases."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )
    assert result.get("type") == FlowResultType.FORM
    assert result.get("errors") == {}
    assert result.get("step_id") == "user"
    assert "flow_id" in result

    mock_smile_config_flow.connect.side_effect = side_effect
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result2.get("type") == FlowResultType.FORM
    assert result2.get("errors") == {"base": reason}
    assert result2.get("step_id") == "user"

    assert len(mock_setup_entry.mock_calls) == 0
    assert len(mock_smile_config_flow.connect.mock_calls) == 1

    mock_smile_config_flow.connect.side_effect = None
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        user_input={CONF_HOST: TEST_HOST, CONF_PASSWORD: TEST_PASSWORD},
    )

    assert result3.get("type") == FlowResultType.CREATE_ENTRY
    assert result3.get("title") == "Test Smile Name"
    assert result3.get("data") == {
        CONF_HOST: TEST_HOST,
        CONF_PASSWORD: TEST_PASSWORD,
        CONF_PORT: DEFAULT_PORT,
        CONF_USERNAME: TEST_USERNAME,
    }

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_smile_config_flow.connect.mock_calls) == 2


async def test_form_cannot_connect_port(
    hass: HomeAssistant, mock_smile: MagicMock
) -> None:
    """Test a connect-failure to an incorrect port."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={CONF_SOURCE: SOURCE_USER},
    )

    mock_smile.connect.side_effect = ConnectionFailedError
    mock_smile.gateway_id = "0a636a4fc1704ab4a24e4f7e37fb187a"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: TEST_HOST,
            CONF_PASSWORD: TEST_PASSWORD,
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_cooling"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_options_flow_thermo(
    hass: HomeAssistant, mock_smile_anna: MagicMock
) -> None:
    """Test config flow options for thermostatic environments."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=CONF_NAME,
        data={
            CONF_HOST: TEST_HOST,
            CONF_PASSWORD: TEST_PASSWORD,
            CONF_TIMEOUT: 30,
        },
        minor_version=2,
        options={
            CONF_HOMEKIT_EMULATION: False,
            CONF_REFRESH_INTERVAL: 1.5,
            CONF_SCAN_INTERVAL: 60,
        },
        version=1,
    )
    entry.runtime_data = MagicMock(api=mock_smile_anna)
    entry.add_to_hass(hass)
    with patch(
        "homeassistant.components.plugwise.async_setup_entry", return_value=True
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={CONF_REFRESH_INTERVAL: 3.0}
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"] == {
            CONF_HOMEKIT_EMULATION: False,
            CONF_REFRESH_INTERVAL: 3.0,
            CONF_SCAN_INTERVAL: 60,
        }


async def _start_reconfigure_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    host_ip: str,
) -> ConfigFlowResult:
    """Initialize a reconfigure flow."""
    mock_config_entry.add_to_hass(hass)

    reconfigure_result = await mock_config_entry.start_reconfigure_flow(hass)

    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    return await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"], {CONF_HOST: host_ip}
    )


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_smile_adam: AsyncMock,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test reconfigure flow."""
    result = await _start_reconfigure_flow(hass, mock_config_entry, TEST_HOST)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    entry = hass.config_entries.async_get_entry(mock_config_entry.entry_id)
    assert entry
    assert entry.data.get(CONF_HOST) == TEST_HOST


async def test_reconfigure_flow_other_smile(
    hass: HomeAssistant,
    mock_smile_adam: AsyncMock,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test reconfigure flow aborts on other Smile ID."""
    mock_smile_adam.smile.hostname = TEST_SMILE_ID

    result = await _start_reconfigure_flow(hass, mock_config_entry, TEST_HOST)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_the_same_smile"


@pytest.mark.parametrize(
    ("side_effect", "reason"),
    [
        (ConnectionFailedError, "cannot_connect"),
        (InvalidAuthentication, "invalid_auth"),
        (InvalidSetupError, "invalid_setup"),
        (InvalidXMLError, "response_error"),
        (RuntimeError, "unknown"),
        (UnsupportedDeviceError, "unsupported"),
    ],
)
async def test_reconfigure_flow_errors(
    hass: HomeAssistant,
    mock_smile_adam: AsyncMock,
    mock_config_entry: MockConfigEntry,
    side_effect: Exception,
    reason: str,
) -> None:
    """Test we handle each reconfigure exception error."""

    mock_smile_adam.connect.side_effect = side_effect

    result = await _start_reconfigure_flow(hass, mock_config_entry, TEST_HOST)

    assert result.get("type") is FlowResultType.FORM
    assert result.get("errors") == {"base": reason}
    assert result.get("step_id") == "reconfigure"
