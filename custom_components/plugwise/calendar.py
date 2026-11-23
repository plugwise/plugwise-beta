"""Calendar platform for Plugwise, with one read-only calendar per schedule."""

from datetime import datetime, timedelta
from typing import Any, override

from plugwise.constants import ScheduleData

from homeassistant.components.calendar import (
    DOMAIN as CALENDAR_DOMAIN,
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.translation import async_get_cached_translations
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LOCATION, LOGGER
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .schedule import PRESETS, expand, switch_points
from .util import plugwise_command

PARALLEL_UPDATES = 0

PRESET_LABEL_KEY = (
    "component.plugwise.entity.climate.plugwise.state_attributes.preset_mode.state.{}"
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Plugwise schedule calendars from a config entry."""
    coordinator = entry.runtime_data
    registry = er.async_get(hass)
    prefix = f"{coordinator.api.gateway_id}-schedule-"
    known: set[str] = set()
    # The first update removes calendars whose schedule was deleted while offline
    registered = {
        entity.unique_id.removeprefix(prefix)
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.domain == CALENDAR_DOMAIN and entity.unique_id.startswith(prefix)
    }

    @callback
    def _update_entities() -> None:
        """Add calendars for new schedules and remove those of deleted ones."""
        gateway = coordinator.data.get(coordinator.api.gateway_id, {})
        if "schedules" not in gateway:
            return
        current = set(gateway["schedules"])
        if new := current - known:
            known.update(new)
            async_add_entities(
                PlugwiseScheduleCalendar(coordinator, rule_id) for rule_id in new
            )
            LOGGER.debug("Add schedule calendars %s", new)
        gone = (known | registered) - current
        known.difference_update(gone)
        registered.clear()
        for rule_id in gone:
            if entity_id := registry.async_get_entity_id(
                CALENDAR_DOMAIN, DOMAIN, prefix + rule_id
            ):
                registry.async_remove(entity_id)

    _update_entities()
    entry.async_on_unload(coordinator.async_add_listener(_update_entities))


class PlugwiseScheduleCalendar(PlugwiseEntity, CalendarEntity):
    """A Plugwise schedule shown as a calendar of its switch points."""

    def __init__(
        self, coordinator: PlugwiseDataUpdateCoordinator, rule_id: str
    ) -> None:
        """Initialise the calendar."""
        super().__init__(coordinator, coordinator.api.gateway_id)
        self.rule_id = rule_id
        self._attr_unique_id = f"{coordinator.api.gateway_id}-schedule-{rule_id}"
        self._labels: dict[str, str] = {}

    @override
    async def async_added_to_hass(self) -> None:
        """Load the preset names in the user's language."""
        await super().async_added_to_hass()
        cached = async_get_cached_translations(
            self.hass, self.hass.config.language, "entity", DOMAIN
        )
        self._labels = {
            preset: cached.get(PRESET_LABEL_KEY.format(preset), preset)
            for preset in PRESETS
        }

    @property
    def schedule(self) -> ScheduleData | None:
        """Return this calendar's schedule, or None when it is gone."""
        return self.device.get("schedules", {}).get(self.rule_id)

    @property
    @override
    def available(self) -> bool:
        """Return whether the schedule still exists."""
        return super().available and self.schedule is not None

    @property
    @override
    def name(self) -> str | None:
        """Return the schedule's name, which can change."""
        return schedule["name"] if (schedule := self.schedule) else None

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the zones the schedule serves and whether it is active."""
        if (schedule := self.schedule) is None:
            return None
        return {"zones": self.zone_names(schedule), "active": schedule["active"]}

    @property
    @override
    def event(self) -> CalendarEvent | None:
        """Return the current or next switch point's event."""
        if not self.available:
            return None
        now = dt_util.as_utc(dt_util.now())
        events = self._events(now, now + timedelta(days=8))
        return next((event for event in events if event.end > now), None)

    @override
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return the events between the two dates."""
        if not self.available:
            return []
        return self._events(start_date, end_date)

    def _events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """Expand the schedule's switch points into events."""
        if (schedule := self.schedule) is None:
            return []
        return expand(
            switch_points(schedule["slots"]),
            start,
            end,
            self._labels,
            dt_util.get_default_time_zone(),
        )

    @plugwise_command
    async def async_set_schedule(
        self, slots: list[dict[str, str | float]], name: str | None
    ) -> None:
        """Replace the schedule's switch points, and rename it when a name is given."""
        await self.coordinator.api.set_schedule(self.rule_id, slots, name=name)

    @plugwise_command
    async def async_delete_schedule(self) -> None:
        """Delete the schedule from the gateway."""
        await self.coordinator.api.delete_schedule(self.rule_id)

    def zone_names(self, schedule: ScheduleData) -> list[str]:
        """Return the names of the zones, also when a thermostat stands for its zone."""
        data = self.coordinator.data
        names = []
        for zone_id in schedule["zones"]:
            # Adam zones are devices; an Anna stands in for its location
            zone = data.get(zone_id) or next(
                (dev for dev in data.values() if dev.get(LOCATION) == zone_id), None
            )
            names.append(zone["name"] if zone and "name" in zone else zone_id)
        return names
