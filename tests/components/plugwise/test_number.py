"""Tests for the Plugwise Number integration."""

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry


async def test_anna_number_entities(
    hass: HomeAssistant, mock_smile_anna: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of a number."""

    # check if the number entity is disabled by default
    assert not hass.states.get("number.opentherm_maximum_boiler_temperature_setpoint")

    # enable number entity
    init_integration.add_to_hass(hass)
    registry = er.async_get(hass)
    registry.async_update_entity(
        "number.opentherm_maximum_boiler_temperature_setpoint", disabled_by=None
    )
    await hass.config_entries.async_reload(init_integration.entry_id)
    await hass.async_block_till_done()

    # Check the number value
    state = hass.states.get("number.opentherm_maximum_boiler_temperature_setpoint")
    assert state
    assert float(state.state) == 60.0
