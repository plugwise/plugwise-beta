"""Plugwise weekly schedules as switch points.

The gateway stores a schedule as slots with a start and an end, but the end is
only the start of another slot. A slot applies from its start until the next
start, and with overlapping slots the latest start wins.
"""

from datetime import UTC, date, datetime, time, timedelta, tzinfo
from typing import Any

from plugwise.constants import SCHEDULE_DAYS, SCHEDULE_POINT, ScheduleSlot

from homeassistant.components.calendar import CalendarEvent

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
PRESETS = ("home", "asleep", "away", "vacation", "no_frost")
MINUTES_PER_DAY = 24 * 60
MINUTES_PER_WEEK = 7 * MINUTES_PER_DAY

type SlotValue = dict[str, str | float]
type SwitchPoint = tuple[int, SlotValue]


def switch_points(slots: list[ScheduleSlot]) -> list[SwitchPoint]:
    """Return a schedule's switch points as week minutes, sorted."""
    points: dict[int, SlotValue] = {}
    for slot in slots:
        # A slot without a readable start has no place in the week
        start = slot.get("start")
        if not isinstance(start, str) or not SCHEDULE_POINT.fullmatch(start):
            continue
        # A later slot with the same start replaces an earlier one
        points[_week_minute(start)] = {
            key: value for key, value in slot.items() if key not in ("start", "end")
        }
    return sorted(points.items())


def expand(
    points: list[SwitchPoint],
    start: datetime,
    end: datetime,
    labels: dict[str, str],
    zone: tzinfo,
) -> list[CalendarEvent]:
    """Return the events overlapping start to end, each lasting until the next point."""
    if not points:
        return []

    events: list[CalendarEvent] = []
    first_day = start.astimezone(zone).date()
    monday = first_day - timedelta(days=first_day.weekday())
    start_timestamp = start.timestamp()
    end_timestamp = end.timestamp()
    week_points = _week_occurrences(points, monday, zone)
    while not any(begin.timestamp() <= start_timestamp for begin, _ in week_points):
        monday -= timedelta(days=7)
        week_points = _week_occurrences(points, monday, zone)

    previous: tuple[datetime, SlotValue] | None = None
    while True:
        for begin, value in week_points:
            begin_timestamp = begin.timestamp()
            if previous is not None:
                previous_begin, previous_value = previous
                finish_timestamp = begin_timestamp
                previous_timestamp = previous_begin.timestamp()
                # Same-zone datetimes compare wall clocks; timestamps compare instants.
                if (
                    finish_timestamp > previous_timestamp
                    and finish_timestamp > start_timestamp
                    and previous_timestamp < end_timestamp
                ):
                    events.append(
                        CalendarEvent(
                            start=previous_begin,
                            end=begin,
                            summary=summary(previous_value, labels),
                        )
                    )
            previous = (begin, value)
            if begin_timestamp >= end_timestamp:
                return events
        monday += timedelta(days=7)
        week_points = _week_occurrences(points, monday, zone)


def summary(value: SlotValue, labels: dict[str, str]) -> str:
    """Return a short text for a switch point's value."""
    if "preset" in value:
        return labels.get(str(value["preset"]), str(value["preset"]))
    if isinstance(setpoint := value.get("setpoint"), float):
        return f"{setpoint:g} °C"
    return ", ".join(f"{key}: {item}" for key, item in value.items())


def to_days(points: list[SwitchPoint]) -> dict[str, list[dict[str, str | float]]]:
    """Return the switch points per day, as used by the schedule actions."""
    days: dict[str, list[dict[str, str | float]]] = {day: [] for day in DAYS}
    for minute, value in points:
        day, rest = divmod(minute, MINUTES_PER_DAY)
        days[DAYS[day]].append({"at": f"{rest // 60:02d}:{rest % 60:02d}", **value})
    return days


def from_days(
    days: dict[str, list[dict[str, Any]]], current: list[SwitchPoint]
) -> list[dict[str, str | float]]:
    """Replace the given days' switch points and return the gateway's slots.

    Days that are not given keep their switch points.
    """
    replaced = {DAYS.index(day) for day in days}
    points: dict[int, SlotValue] = {
        minute: value
        for minute, value in current
        if minute // MINUTES_PER_DAY not in replaced
    }
    for day, entries in days.items():
        for entry in entries:
            at = _clock_minute(entry["at"])
            points[DAYS.index(day) * MINUTES_PER_DAY + at] = {
                key: item for key, item in entry.items() if key != "at"
            }

    if len(points) < 2:
        raise ValueError("a schedule needs at least two switch points")

    ordered = sorted(points.items())
    return [
        {
            "start": _notation(minute),
            "end": _notation(ordered[(index + 1) % len(ordered)][0]),
            **value,
        }
        for index, (minute, value) in enumerate(ordered)
    ]


def _week_minute(point: str) -> int:
    """Convert "mo 07:15" to minutes since Monday 00:00."""
    day, clock = point.split(" ")
    return SCHEDULE_DAYS.index(day) * MINUTES_PER_DAY + _clock_minute(clock)


def _clock_minute(clock: str | time) -> int:
    """Convert "07:15", "07:15:00" or a time to minutes since midnight."""
    if isinstance(clock, time):
        return clock.hour * 60 + clock.minute
    hours, minutes = clock.split(":")[:2]
    return int(hours) * 60 + int(minutes)


def _notation(minute: int) -> str:
    """Convert minutes since Monday 00:00 to "mo 07:15"."""
    day, rest = divmod(minute, MINUTES_PER_DAY)
    return f"{SCHEDULE_DAYS[day]} {rest // 60:02d}:{rest % 60:02d}"


def _at(monday: date, minute: int, zone: tzinfo) -> datetime:
    """Return the local time the given number of minutes after Monday's midnight."""
    day, rest = divmod(minute, MINUTES_PER_DAY)
    return datetime.combine(
        monday + timedelta(days=day), time(rest // 60, rest % 60), tzinfo=zone
    )


def _week_occurrences(
    points: list[SwitchPoint], monday: date, zone: tzinfo
) -> list[tuple[datetime, SlotValue]]:
    """Return the switch points whose local times exist in this week."""
    return [
        (_at(monday, minute, zone), value)
        for minute, value in points
        if _is_valid_local_time(monday, minute, zone)
    ]


def _is_valid_local_time(monday: date, minute: int, zone: tzinfo) -> bool:
    """Return whether a local schedule time exists in this week's timezone."""
    local = _at(monday, minute, zone)
    round_trip = local.astimezone(UTC).astimezone(zone)
    return round_trip.replace(tzinfo=None) == local.replace(tzinfo=None)
