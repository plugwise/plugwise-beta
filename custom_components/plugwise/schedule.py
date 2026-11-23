"""Plugwise weekly schedules as switch points.

The gateway stores a schedule as slots with a start and an end, but the end is
only the start of another slot. A slot applies from its start until the next
start, and with overlapping slots the latest start wins.
"""

from datetime import date, datetime, time, timedelta, tzinfo

from plugwise.constants import SCHEDULE_DAYS, SCHEDULE_POINT, ScheduleSlot

from homeassistant.components.calendar import CalendarEvent

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
    # Begin a week early: the last point of the previous week runs into this one
    monday = first_day - timedelta(days=first_day.weekday() + 7)
    while _at(monday, 0, zone) < end:
        for index, (minute, value) in enumerate(points):
            if index + 1 < len(points):
                next_minute = points[index + 1][0]
            else:
                next_minute = points[0][0] + MINUTES_PER_WEEK
            begin = _at(monday, minute, zone)
            finish = _at(monday, next_minute, zone)
            # A point in the hour that daylight saving time skips has no length.
            # Timestamps compare instants, but same-zone datetimes compare wall clocks.
            if (
                finish.timestamp() <= begin.timestamp()
                or finish <= start
                or begin >= end
            ):
                continue
            events.append(
                CalendarEvent(start=begin, end=finish, summary=summary(value, labels))
            )
        monday += timedelta(days=7)
    return events


def summary(value: SlotValue, labels: dict[str, str]) -> str:
    """Return a short text for a switch point's value."""
    if "preset" in value:
        return labels.get(str(value["preset"]), str(value["preset"]))
    if isinstance(setpoint := value.get("setpoint"), float):
        return f"{setpoint:g} °C"
    return ", ".join(f"{key}: {item}" for key, item in value.items())


def _week_minute(point: str) -> int:
    """Convert "mo 07:15" to minutes since Monday 00:00."""
    day, clock = point.split(" ")
    return SCHEDULE_DAYS.index(day) * MINUTES_PER_DAY + _clock_minute(clock)


def _clock_minute(clock: str) -> int:
    """Convert "07:15" to minutes since midnight."""
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def _at(monday: date, minute: int, zone: tzinfo) -> datetime:
    """Return the local time the given number of minutes after Monday's midnight."""
    day, rest = divmod(minute, MINUTES_PER_DAY)
    return datetime.combine(
        monday + timedelta(days=day), time(rest // 60, rest % 60), tzinfo=zone
    )
