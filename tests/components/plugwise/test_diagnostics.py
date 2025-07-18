"""Tests for the diagnostics data provided by the Plugwise integration."""
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


async def test_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_smile_adam: MagicMock,
    init_integration: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test diagnostics."""

    assert (
        await get_diagnostics_for_config_entry(hass, hass_client, init_integration)
        == snapshot
    )
