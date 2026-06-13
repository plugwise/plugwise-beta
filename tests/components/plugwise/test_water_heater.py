"""Tests for the Plugwise water_heater platform."""

from unittest.mock import MagicMock

import pytest

from homeassistant.components.water_heater import (
    DOMAIN as WATER_HEATER_DOMAIN,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion

from tests.common import MockConfigEntry, snapshot_platform

HA_PLUGWISE_SMILE_ASYNC_UPDATE = (
    "homeassistant.components.plugwise.coordinator.Smile.async_update"
)


@pytest.mark.parametrize("platforms", [(WATER_HEATER_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_adam_water_heater_snapshot(
    hass: HomeAssistant,
    mock_smile_adam_jip: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Adam water_heater snapshot with dhw_state off."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


async def test_adam_water_heater_setpoint_change(
    hass: HomeAssistant, mock_smile_adam_jip: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test Adam water_heater setpoint-change."""
    await hass.services.async_call(
        WATER_HEATER_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: "water_heater.opentherm", ATTR_TEMPERATURE: 65},
        blocking=True,
    )
    assert mock_smile_adam_jip.set_number.call_count == 1
    mock_smile_adam_jip.set_number.assert_called_with(
        "e4684553153b44afbef2200885f379dc", "max_dhw_temperature", 65.0,
    )


@pytest.mark.parametrize("chosen_env", ["anna_v4_dhw"], indirect=True)
@pytest.mark.parametrize("cooling_present", [False], indirect=True)
@pytest.mark.parametrize("platforms", [(WATER_HEATER_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_anna_water_heater_snapshot(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Anna water_heater snapshot with dhw_state on."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)
