"""Services for the Plugwise-beta integration."""

from typing import Any, cast

from plugwise.constants import ScheduleData
from plugwise.exceptions import PlugwiseError, PlugwiseException

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, selector, service
import probatio

from .calendar import PlugwiseScheduleCalendar
from .const import (
    CONFIG_ENTRY,
    DOMAIN,
    LOGGER,
    SERVICE_DELETE,  # pw-beta delete_notifications
)
from .coordinator import PlugwiseConfigEntry
from .schedule import DAYS, PRESETS, from_days, switch_points, to_days

SCHEMA_DELETE_NOTIFICATION = probatio.Schema(
    {
        probatio.Required(CONFIG_ENTRY): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            }
        )
    }
)

SWITCH_POINT_SCHEMA = probatio.Schema(
    {
        probatio.Required("at"): cv.time,
        probatio.Optional("preset"): probatio.In(PRESETS),
        probatio.Optional("setpoint"): probatio.All(
            probatio.Coerce(float), probatio.Range(min=4, max=30)
        ),
    }
)
DAY_FIELDS = {probatio.Optional(day): [SWITCH_POINT_SCHEMA] for day in DAYS}
SCHEMA_CHANGE_SCHEDULE = {probatio.Optional("name"): cv.string, **DAY_FIELDS}
SCHEMA_CREATE_SCHEDULE = probatio.Schema(
    {
        probatio.Required(CONFIG_ENTRY): selector.ConfigEntrySelector(
            {"integration": DOMAIN}
        ),
        probatio.Required("name"): cv.string,
        **DAY_FIELDS,
    }
)


def _days(call: ServiceCall) -> dict[str, list[dict[str, Any]]]:
    """Return the given days' switch points, checked beyond what the schema can."""
    days = {day: call.data[day] for day in DAYS if day in call.data}
    for points in days.values():
        # The gateway keeps minutes, so seconds cannot tell two points apart
        times = [(point["at"].hour, point["at"].minute) for point in points]
        if len(times) != len(set(times)):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="schedule_duplicate_time",
            )
        if any(("preset" in point) == ("setpoint" in point) for point in points):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="schedule_preset_or_setpoint",
            )
    return days


def _slots(
    days: dict[str, list[dict[str, Any]]], current: list[Any]
) -> list[dict[str, str | float]]:
    """Return the gateway slots, refusing a week with fewer than two switch points."""
    try:
        return from_days(days, current)
    except ValueError as err:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="schedule_too_few_points"
        ) from err


async def get_schedule(
    entity: PlugwiseScheduleCalendar, call: ServiceCall
) -> ServiceResponse:
    """Return a schedule's switch points per day."""
    # Home Assistant only calls available calendars, which have a schedule
    schedule = cast(ScheduleData, entity.schedule)
    response = {
        "name": schedule["name"],
        "zones": entity.zone_names(schedule),
        **to_days(switch_points(schedule["slots"])),
    }
    return cast(ServiceResponse, response)


async def change_schedule(entity: PlugwiseScheduleCalendar, call: ServiceCall) -> None:
    """Update/replace the switch points of the given days, and rename when asked."""
    days = _days(call)
    async with entity.schedule_lock:
        # Days left out are written back, so read them fresh from the gateway
        coordinator = entity.coordinator
        await coordinator.async_refresh()
        if not coordinator.last_update_success:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="error_communicating_with_api",
                translation_placeholders={"error": str(coordinator.last_exception)},
            )
        if (schedule := entity.schedule) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="schedule_not_found"
            )
        current = switch_points(schedule["slots"])
        # Slots with other settings, or a setpoint that is not a number, cannot be
        # written back unchanged
        if any(
            set(value) - {"preset", "setpoint"}
            or not isinstance(value.get("setpoint", 0.0), float)
            for _, value in current
        ):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="schedule_other_settings"
            )
        slots = _slots(days, current)
        await entity.async_update_schedule(slots, call.data.get("name"))


async def delete_schedule(entity: PlugwiseScheduleCalendar, call: ServiceCall) -> None:
    """Delete a schedule from the gateway."""
    await entity.async_delete_schedule()


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Plugwise-beta services."""

    async def delete_notification(
        call: ServiceCall,
    ) -> None:  # pragma: no cover  # pw-beta: HA service - delete_notification
        """Service: delete the Plugwise Notification."""

        entry: PlugwiseConfigEntry = service.async_get_config_entry(
            call.hass, DOMAIN, call.data[CONFIG_ENTRY]
        )
        coordinator = entry.runtime_data

        LOGGER.debug(
            "Service delete PW Notification called for %s",
            coordinator.api.smile.name,
        )
        try:
            await coordinator.api.delete_notification()
            LOGGER.debug("PW Notification deleted")
        except PlugwiseError:
            LOGGER.debug(
                "Failed to delete the Plugwise Notification for %s",
                coordinator.api.smile.name,
            )

    async def create_schedule(call: ServiceCall) -> None:
        """Create a schedule that is not linked to any zone yet."""
        entry: PlugwiseConfigEntry = service.async_get_config_entry(
            call.hass, DOMAIN, call.data[CONFIG_ENTRY]
        )
        coordinator = entry.runtime_data
        slots = _slots(_days(call), [])
        try:
            await coordinator.api.create_schedule(call.data["name"], slots)
        except PlugwiseException as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="error_communicating_with_api",
                translation_placeholders={"error": str(err)},
            ) from err
        finally:
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE,
        delete_notification,
        schema=SCHEMA_DELETE_NOTIFICATION
    )
    hass.services.async_register(
        DOMAIN, "create_schedule", create_schedule, schema=SCHEMA_CREATE_SCHEDULE
    )
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        "get_schedule",
        entity_domain=CALENDAR_DOMAIN,
        schema=None,
        supports_response=SupportsResponse.ONLY,
        func=get_schedule,
    )
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        "change_schedule",
        entity_domain=CALENDAR_DOMAIN,
        schema=cv.make_entity_service_schema(SCHEMA_CHANGE_SCHEDULE),
        supports_response=SupportsResponse.NONE,
        func=change_schedule,
    )
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        "delete_schedule",
        entity_domain=CALENDAR_DOMAIN,
        schema=None,
        supports_response=SupportsResponse.NONE,
        func=delete_schedule,
    )

