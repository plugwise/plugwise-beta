"""Tests for the Plugwise schedule calendars."""

from datetime import timedelta
from itertools import pairwise
from unittest.mock import MagicMock, patch

import pytest

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.calendar import (
    DOMAIN as CALENDAR_DOMAIN,
    EVENT_END_DATETIME,
    EVENT_START_DATETIME,
    SERVICE_GET_EVENTS,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion

from pytest_homeassistant.common import (
    MockConfigEntry,
    async_fire_time_changed,
    snapshot_platform,
)

GATEWAY = "fe799307f1624099878210aa0b9f1475"
BATHROOM_SCHEDULE = "3e4b5a775f8143de961eaa3f5f7d9d1a"
HA_PLUGWISE_SMILE_ASYNC_UPDATE = (
    "homeassistant.components.plugwise.coordinator.Smile.async_update"
)


@pytest.mark.usefixtures("mock_smile_adam", "entity_registry_enabled_by_default")
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
@pytest.mark.freeze_time("2026-10-26 07:00:00-07:00")
async def test_adam_calendar_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test one calendar per Adam schedule."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


@pytest.mark.usefixtures("mock_smile_adam")
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
@pytest.mark.freeze_time("2026-10-26 07:00:00-07:00")
async def test_adam_calendar_events(
    hass: HomeAssistant, setup_platform: MockConfigEntry
) -> None:
    """Test the events and state of a schedule calendar on a Monday."""
    entity_id = "calendar.adam_badkamer_schema"
    # Monday 06:45 home started a quarter of an hour ago
    assert hass.states.get(entity_id).state == "on"
    assert hass.states.get(entity_id).attributes["message"] == "Home"
    assert hass.states.get(entity_id).attributes["zones"] == ["Badkamer"]

    response = await hass.services.async_call(
        CALENDAR_DOMAIN,
        SERVICE_GET_EVENTS,
        {
            ATTR_ENTITY_ID: entity_id,
            EVENT_START_DATETIME: "2026-10-26T00:00:00-07:00",
            EVENT_END_DATETIME: "2026-10-27T00:00:00-07:00",
        },
        blocking=True,
        return_response=True,
    )
    events = [
        (event["start"], event["end"], event["summary"])
        for event in response[entity_id]["events"]
    ]
    assert ("2026-10-26T06:45:00-07:00", "2026-10-26T08:00:00-07:00", "Home") in events
    # Each switch point lasts until the next one, without gaps
    assert all(a[1] == b[0] for a, b in pairwise(events))


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_adam_calendar_added_and_removed(
    hass: HomeAssistant,
    mock_smile_adam: MagicMock,
    setup_platform: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that schedules appearing and disappearing add and remove calendars."""
    data = mock_smile_adam.async_update.return_value
    entity_id = "calendar.adam_badkamer_schema"
    assert entity_registry.async_get(entity_id) is not None

    removed = data[GATEWAY]["schedules"].pop(BATHROOM_SCHEDULE)
    data[GATEWAY]["schedules"]["0" * 32] = {**removed, "name": "Nieuw"}
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

    assert entity_registry.async_get(entity_id) is None
    assert hass.states.get("calendar.adam_nieuw") is not None


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_adam_calendars_kept_without_schedules_data(
    hass: HomeAssistant,
    mock_smile_adam: MagicMock,
    setup_platform: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that an update without schedules data removes no calendars."""
    data = mock_smile_adam.async_update.return_value
    del data[GATEWAY]["schedules"]
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

    assert entity_registry.async_get("calendar.adam_badkamer_schema") is not None


@pytest.mark.usefixtures("mock_smile_adam")
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_adam_calendar_of_deleted_schedule_removed_at_setup(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    platforms: tuple[str, ...],
) -> None:
    """Test that a calendar left from a schedule deleted while offline is removed."""
    mock_config_entry.add_to_hass(hass)
    stale = entity_registry.async_get_or_create(
        CALENDAR_DOMAIN,
        "plugwise",
        f"{GATEWAY}-schedule-{'1' * 32}",
        config_entry=mock_config_entry,
    )
    with patch("homeassistant.components.plugwise.PLATFORMS", platforms):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert entity_registry.async_get(stale.entity_id) is None
    assert entity_registry.async_get("calendar.adam_badkamer_schema") is not None


@pytest.mark.usefixtures("mock_smile_p1")
@pytest.mark.parametrize("chosen_env", ["p1v4_442_single"], indirect=True)
@pytest.mark.parametrize(
    "gateway_id", ["a455b61e52394b2db5081ce025a430f3"], indirect=True
)
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_p1_has_no_calendars(
    hass: HomeAssistant, setup_platform: MockConfigEntry
) -> None:
    """Test that a gateway without schedules gets no calendars."""
    assert hass.states.async_entity_ids(CALENDAR_DOMAIN) == []
