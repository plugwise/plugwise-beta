"""Tests for the Plugwise schedule helpers."""

from datetime import datetime, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from homeassistant.components.plugwise.schedule import (
    expand,
    from_days,
    summary,
    switch_points,
    to_days,
)

AMSTERDAM = ZoneInfo("Europe/Amsterdam")
FIXTURES = Path(__file__).parent / "fixtures"


def _fixture_schedules() -> list[dict]:
    """Return every schedule in the test fixtures."""
    schedules = []
    for path in sorted(FIXTURES.glob("*/data.json")):
        for device in json.loads(path.read_text()).values():
            schedules.extend(device.get("schedules", {}).values())
    return schedules


def test_round_trip_all_fixture_schedules() -> None:
    """Test that every fixture schedule survives per-day lists unchanged."""
    schedules = [s for s in _fixture_schedules() if len(switch_points(s["slots"])) > 1]
    assert schedules
    for schedule in schedules:
        points = switch_points(schedule["slots"])
        assert switch_points(from_days(to_days(points), [])) == points


def test_overlapping_slots_are_switch_points() -> None:
    """Test that overlapping slots become consecutive switch points."""
    slots = [
        {"start": "tu 10:00", "end": "th 10:00", "setpoint": 16.0},
        {"start": "mo 10:00", "end": "we 10:00", "setpoint": 15.0},
    ]
    points = switch_points(slots)
    assert points == [(600, {"setpoint": 15.0}), (2040, {"setpoint": 16.0})]

    monday = datetime(2026, 10, 26, tzinfo=AMSTERDAM)
    events = expand(points, monday, monday + timedelta(days=7), {}, AMSTERDAM)
    # The first event started in the previous week and runs into this one
    assert [
        (e.start.strftime("%a %d %H:%M"), e.end.strftime("%a %d %H:%M"), e.summary)
        for e in events
    ] == [
        ("Tue 20 10:00", "Mon 26 10:00", "16 °C"),
        ("Mon 26 10:00", "Tue 27 10:00", "15 °C"),
        ("Tue 27 10:00", "Mon 02 10:00", "16 °C"),
    ]


def test_same_start_later_slot_wins() -> None:
    """Test that a later slot with the same start replaces an earlier one."""
    slots = [
        {"start": "mo 07:00", "end": "mo 22:00", "preset": "away"},
        {"start": "mo 07:00", "end": "mo 22:00", "preset": "home"},
        {"start": "mo 22:00", "end": "mo 07:00", "preset": "asleep"},
    ]
    assert switch_points(slots) == [
        (420, {"preset": "home"}),
        (1320, {"preset": "asleep"}),
    ]


def test_daylight_saving_hour_is_skipped() -> None:
    """Test that a switch point in the skipped hour gives no event."""
    points = switch_points(
        [
            {"start": "mo 00:00", "preset": "asleep"},
            {"start": "su 02:00", "preset": "home"},
            {"start": "su 03:00", "preset": "away"},
        ]
    )
    dst_sunday = datetime(2027, 3, 28, tzinfo=AMSTERDAM)
    events = expand(points, dst_sunday, dst_sunday + timedelta(days=1), {}, AMSTERDAM)
    assert [e.summary for e in events] == ["asleep", "away"]

    next_sunday = dst_sunday + timedelta(days=7)
    labels = {"home": "Home"}
    events = expand(
        points, next_sunday, next_sunday + timedelta(days=1), labels, AMSTERDAM
    )
    assert [e.summary for e in events] == ["asleep", "Home", "away"]


def test_no_switch_points_no_events() -> None:
    """Test that a schedule without slots has no events."""
    start = datetime(2026, 10, 26, tzinfo=AMSTERDAM)
    assert expand([], start, start + timedelta(days=7), {}, AMSTERDAM) == []


def test_summary_of_other_settings() -> None:
    """Test the summary of a switch point without a preset or setpoint."""
    assert summary({"heating_setpoint": 20.0}, {}) == "heating_setpoint: 20.0"


def test_slot_without_start_is_skipped() -> None:
    """Test that a slot the library could not read does not break the schedule."""
    slots = [
        {"time": "[xx 07:00,mo 22:00)", "preset": "home"},
        {"start": "mo 22:00", "end": "mo 07:00", "preset": "asleep"},
    ]
    assert switch_points(slots) == [(1320, {"preset": "asleep"})]


def test_slot_with_unknown_day_is_skipped() -> None:
    """Test that a start with a day code the week does not have is skipped."""
    slots = [
        {"start": "xx 07:00", "end": "mo 22:00", "preset": "home"},
        {"start": "mo 22:00", "end": "mo 07:00", "preset": "asleep"},
    ]
    assert switch_points(slots) == [(1320, {"preset": "asleep"})]


def test_summary_of_unreadable_setpoint() -> None:
    """Test that a setpoint the library kept as text is shown as text."""
    assert summary({"setpoint": "abc"}, {}) == "setpoint: abc"


def test_from_days_replaces_given_days_only() -> None:
    """Test that only the given days change and the week is closed again."""
    points = switch_points(
        [
            {"start": "mo 07:00", "preset": "home"},
            {"start": "mo 22:00", "preset": "asleep"},
            {"start": "tu 07:00", "preset": "home"},
        ]
    )
    slots = from_days({"monday": [{"at": "08:00", "preset": "away"}]}, points)
    assert slots == [
        {"start": "mo 08:00", "end": "tu 07:00", "preset": "away"},
        {"start": "tu 07:00", "end": "mo 08:00", "preset": "home"},
    ]


def test_from_days_needs_two_switch_points() -> None:
    """Test that a week with one switch point is refused."""
    with pytest.raises(ValueError):
        from_days({"monday": [{"at": "07:00", "preset": "home"}]}, [])
