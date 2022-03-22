"""Tests for the Plugwise Number integration."""

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_anna_number_entities(
    hass: HomeAssistant, mock_smile_anna: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of a number."""
    state = hass.states.get("number.opentherm_maximum_boiler_temperature_setpoint")
    assert state
    assert float(state.state) == 60.0