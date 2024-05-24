"""Tests for Plugwise button entities."""

from unittest.mock import MagicMock

from homeassistant.components.button import ButtonDeviceClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ENTITY_ID,
    STATE_UNKNOWN,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry


async def test_adam_reboot_button(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of button entities."""
    state = hass.states.get("button.adam_reboot")
    assert state
    assert state.state == STATE_UNKNOWN
    assert state.attributes.get(ATTR_DEVICE_CLASS) == ButtonDeviceClass.RESTART

    registry = er.async_get(hass)
    entry = registry.async_get("button.adam_reboot")
    assert entry
    assert entry.unique_id == "fe799307f1624099878210aa0b9f1475-reboot"

    await hass.services.async_call(
        Platform.BUTTON,
        "press",
        {ATTR_ENTITY_ID: "button.adam_reboot"},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert mock_smile_adam.reboot_gateway.call_count == 1
    mock_smile_adam.reboot_gateway.assert_called_with()
