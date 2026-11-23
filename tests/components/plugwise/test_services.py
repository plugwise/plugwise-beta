"""Tests for the Plugwise schedule actions."""

from copy import deepcopy
from unittest.mock import MagicMock

from plugwise.exceptions import ConnectionFailedError
import pytest

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.components.plugwise.const import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from syrupy.assertion import SnapshotAssertion

from pytest_homeassistant.common import MockConfigEntry

BATHROOM = "calendar.adam_badkamer_schema"
BATHROOM_SCHEDULE = "3e4b5a775f8143de961eaa3f5f7d9d1a"
GATEWAY = "fe799307f1624099878210aa0b9f1475"


@pytest.mark.usefixtures("mock_smile_adam")
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_get_schedule(
    hass: HomeAssistant, setup_platform: MockConfigEntry, snapshot: SnapshotAssertion
) -> None:
    """Test reading a schedule's switch points per day."""
    response = await hass.services.async_call(
        DOMAIN,
        "get_schedule",
        {ATTR_ENTITY_ID: BATHROOM},
        blocking=True,
        return_response=True,
    )
    assert response[BATHROOM]["name"] == "Badkamer Schema"
    assert response[BATHROOM]["zones"] == ["Badkamer"]
    assert response == snapshot


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test replacing one day's switch points and renaming."""
    await hass.services.async_call(
        DOMAIN,
        "set_schedule",
        {
            ATTR_ENTITY_ID: BATHROOM,
            "name": "Badkamer",
            "monday": [
                {"at": "07:00", "preset": "home"},
                {"at": "22:00", "setpoint": 16.5},
            ],
        },
        blocking=True,
    )
    rule_id, slots = mock_smile_adam.set_schedule.call_args.args
    assert rule_id == BATHROOM_SCHEDULE
    assert mock_smile_adam.set_schedule.call_args.kwargs == {"name": "Badkamer"}
    monday = [slot for slot in slots if str(slot["start"]).startswith("mo ")]
    assert monday == [
        {"start": "mo 07:00", "end": "mo 22:00", "preset": "home"},
        {"start": "mo 22:00", "end": monday[1]["end"], "setpoint": 16.5},
    ]
    # Tuesday keeps its switch points, so Monday 22:00 lasts until Tuesday
    assert monday[1]["end"].startswith("tu ")


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule_reads_the_gateway_first(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that a day changed on the gateway since the last update is kept."""
    data = deepcopy(mock_smile_adam.async_update.return_value)
    data[GATEWAY]["schedules"][BATHROOM_SCHEDULE]["slots"].append(
        {"start": "tu 12:34", "end": "tu 13:00", "preset": "away"}
    )
    mock_smile_adam.async_update.return_value = data
    await hass.services.async_call(
        DOMAIN,
        "set_schedule",
        {ATTR_ENTITY_ID: BATHROOM, "monday": [{"at": "07:00", "preset": "home"}]},
        blocking=True,
    )
    _, slots = mock_smile_adam.set_schedule.call_args.args
    assert any(slot["start"] == "tu 12:34" for slot in slots)


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule_deleted_on_the_gateway(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that a schedule deleted since the last update is not written back."""
    data = deepcopy(mock_smile_adam.async_update.return_value)
    del data[GATEWAY]["schedules"][BATHROOM_SCHEDULE]
    mock_smile_adam.async_update.return_value = data
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {ATTR_ENTITY_ID: BATHROOM, "name": "Other"},
            blocking=True,
        )
    assert err.value.translation_key == "schedule_not_found"
    mock_smile_adam.set_schedule.assert_not_called()


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule_invalid_input_skips_the_gateway(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that invalid switch points are refused without reading the gateway."""
    mock_smile_adam.async_update.reset_mock()
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {ATTR_ENTITY_ID: BATHROOM, "monday": [{"at": "07:00"}]},
            blocking=True,
        )
    mock_smile_adam.async_update.assert_not_called()


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule_gateway_unreachable(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that nothing is written when the gateway cannot be read first."""
    mock_smile_adam.async_update.side_effect = ConnectionFailedError
    with pytest.raises(HomeAssistantError) as err:
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {ATTR_ENTITY_ID: BATHROOM, "name": "Other"},
            blocking=True,
        )
    assert err.value.translation_key == "error_communicating_with_api"
    mock_smile_adam.set_schedule.assert_not_called()


@pytest.mark.usefixtures("mock_smile_adam")
@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
@pytest.mark.parametrize(
    ("monday", "translation_key"),
    [
        (
            [{"at": "07:00", "preset": "home"}, {"at": "07:00", "preset": "away"}],
            "schedule_duplicate_time",
        ),
        (
            [{"at": "07:00", "preset": "home", "setpoint": 18}],
            "schedule_preset_or_setpoint",
        ),
        ([{"at": "07:00"}], "schedule_preset_or_setpoint"),
        (
            [
                {"at": "07:00:00", "preset": "home"},
                {"at": "07:00:30", "preset": "away"},
            ],
            "schedule_duplicate_time",
        ),
    ],
)
async def test_set_schedule_invalid(
    hass: HomeAssistant,
    setup_platform: MockConfigEntry,
    monday: list,
    translation_key: str,
) -> None:
    """Test that invalid switch points are refused before anything is sent."""
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {ATTR_ENTITY_ID: BATHROOM, "monday": monday},
            blocking=True,
        )
    assert err.value.translation_key == translation_key


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_set_schedule_too_few_switch_points(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that emptying the week down to one switch point is refused."""
    days = {
        day: []
        for day in ("tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    }
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {
                ATTR_ENTITY_ID: BATHROOM,
                "monday": [{"at": "07:00", "preset": "home"}],
                **days,
            },
            blocking=True,
        )
    assert err.value.translation_key == "schedule_too_few_points"
    mock_smile_adam.set_schedule.assert_not_called()


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
@pytest.mark.parametrize(
    "setting",
    [
        pytest.param({"heating_setpoint": 20.0}, id="other_setting"),
        pytest.param({"setpoint": "nan"}, id="unreadable_setpoint"),
    ],
)
async def test_set_schedule_other_settings(
    hass: HomeAssistant,
    mock_smile_adam: MagicMock,
    setup_platform: MockConfigEntry,
    setting: dict[str, str | float],
) -> None:
    """Test that a schedule with settings the actions cannot express is not changed."""
    schedule = mock_smile_adam.async_update.return_value[GATEWAY]["schedules"][
        BATHROOM_SCHEDULE
    ]
    schedule["slots"][0] = {**schedule["slots"][0], **setting}
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            "set_schedule",
            {ATTR_ENTITY_ID: BATHROOM, "name": "Other"},
            blocking=True,
        )
    assert err.value.translation_key == "schedule_other_settings"
    mock_smile_adam.set_schedule.assert_not_called()


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_create_and_delete_schedule(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test creating a schedule on the gateway and deleting one."""
    await hass.services.async_call(
        DOMAIN,
        "create_schedule",
        {
            "config_entry": setup_platform.entry_id,
            "name": "Nieuw",
            "monday": [{"at": "07:00", "preset": "home"}],
            "friday": [{"at": "23:00", "preset": "asleep"}],
        },
        blocking=True,
    )
    mock_smile_adam.create_schedule.assert_called_once_with(
        "Nieuw",
        [
            {"start": "mo 07:00", "end": "fr 23:00", "preset": "home"},
            {"start": "fr 23:00", "end": "mo 07:00", "preset": "asleep"},
        ],
    )

    await hass.services.async_call(
        DOMAIN, "delete_schedule", {ATTR_ENTITY_ID: BATHROOM}, blocking=True
    )
    mock_smile_adam.delete_schedule.assert_called_once_with(BATHROOM_SCHEDULE)


@pytest.mark.parametrize("platforms", [(CALENDAR_DOMAIN,)])
async def test_create_schedule_gateway_error(
    hass: HomeAssistant, mock_smile_adam: MagicMock, setup_platform: MockConfigEntry
) -> None:
    """Test that a gateway error while creating a schedule is reported."""
    mock_smile_adam.create_schedule.side_effect = ConnectionFailedError
    with pytest.raises(HomeAssistantError) as err:
        await hass.services.async_call(
            DOMAIN,
            "create_schedule",
            {
                "config_entry": setup_platform.entry_id,
                "name": "Nieuw",
                "monday": [{"at": "07:00", "preset": "home"}],
                "friday": [{"at": "23:00", "preset": "asleep"}],
            },
            blocking=True,
        )
    assert err.value.translation_key == "error_communicating_with_api"
