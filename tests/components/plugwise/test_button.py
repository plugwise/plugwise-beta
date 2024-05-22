"""Tests for Plugwise button entities."""

from unittest.mock import MagicMock

from homeassistant.const import ATTR_DEVICE_CLASS, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import async_update_entity

from tests.common import MockConfigEntry


async def test_adam_reboot_button(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of button entities."""
    state = hass.states.get("button.adam_reboot")
    assert state
    assert state.state == STATE_UNKNOWN
    assert state.attributes.get(ATTR_DEVICE_CLASS) == ButtonDeviceClass.RESTART

    # registry = er.async_get(hass)
    # entry = registry.async_get("button.adam_restart")
    # assert entry
    # assert entry.unique_id == f"{MAC}_reboot"
    #
    # await hass.services.async_call(
    #     BUTTON_DOMAIN,
    #     "press",
    #     {ATTR_ENTITY_ID: "button.adam_restart"},
    #     blocking=True,
    # )
    # await hass.async_block_till_done()
    #
    # Test if called
    