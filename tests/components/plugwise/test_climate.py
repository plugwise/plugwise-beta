"""Tests for the Plugwise Climate integration."""

from datetime import timedelta
import math
from unittest.mock import MagicMock, patch

from plugwise.exceptions import PlugwiseError
import pytest

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.climate import (
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACMode,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from tests.common import MockConfigEntry, async_fire_time_changed

HA_PLUGWISE_SMILE_ASYNC_UPDATE = (
    "homeassistant.components.plugwise.coordinator.Smile.async_update"
)
TEST_HOST = "1.1.1.1"
TEST_PASSWORD = "test_password"


async def test_adam_climate_entity_attributes(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of adam climate device environment."""
    state = hass.states.get("climate.woonkamer")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "heating"
    assert state.attributes["hvac_modes"] == [
        HVACMode.AUTO,
        HVACMode.HEAT,
    ]
    assert "preset_modes" in state.attributes
    assert "no_frost" in state.attributes["preset_modes"]
    assert "home" in state.attributes["preset_modes"]

    assert state.attributes["current_temperature"] == 20.9
    assert state.attributes["preset_mode"] == "home"
    assert state.attributes["supported_features"] == 17
    assert state.attributes["temperature"] == 21.5
    assert state.attributes["min_temp"] == 0.0
    assert state.attributes["max_temp"] == 35
    assert math.isclose(
        state.attributes["target_temp_step"], 0.1, rel_tol=1e-09, abs_tol=1e-09
    )

    state = hass.states.get("climate.jessie")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "idle"
    assert state.attributes["hvac_modes"] == [
        HVACMode.AUTO,
        HVACMode.HEAT,
    ]
    assert "preset_modes" in state.attributes
    assert "no_frost" in state.attributes["preset_modes"]
    assert "home" in state.attributes["preset_modes"]

    assert state.attributes["current_temperature"] == 17.2
    assert state.attributes["preset_mode"] == "asleep"
    assert state.attributes["temperature"] == 15.0
    assert state.attributes["min_temp"] == 0.0
    assert state.attributes["max_temp"] == 35
    assert math.isclose(
        state.attributes["target_temp_step"], 0.1, rel_tol=1e-09, abs_tol=1e-09
    )


@pytest.mark.parametrize("chosen_env", ["m_adam_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [False], indirect=True)
async def test_adam_2_climate_entity_attributes(
    hass: HomeAssistant, mock_smile_adam_heat_cool: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of adam climate device environment."""
    state = hass.states.get("climate.living_room")
    assert state
    assert state.state == HVACMode.HEAT
    assert state.attributes["hvac_action"] == "preheating"
    assert state.attributes["hvac_modes"] == [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
    ]

    state = hass.states.get("climate.bathroom")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "idle"
    assert state.attributes["hvac_modes"] == [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.HEAT,
    ]


@pytest.mark.parametrize("chosen_env", ["m_adam_cooling"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_adam_3_climate_entity_attributes(
    hass: HomeAssistant,
    mock_smile_adam_heat_cool: MagicMock,
    init_integration: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test creation of adam climate device environment."""
    state = hass.states.get("climate.living_room")
    assert state
    assert state.state == HVACMode.COOL
    assert state.attributes["hvac_action"] == "cooling"
    assert state.attributes["hvac_modes"] == [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.COOL,
    ]

    data = mock_smile_adam_heat_cool.async_update.return_value
    data["da224107914542988a88561b4452b0f6"][
        "select_regulation_mode"
    ] = "heating"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["control_state"] = "heating"
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"][
        "cooling_state"
    ] = False
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"][
        "heating_state"
    ] = True
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.living_room")
        assert state
        assert state.state == HVACMode.HEAT
        assert state.attributes["hvac_action"] == "heating"
        assert state.attributes["hvac_modes"] == [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.HEAT,
        ]

    data = mock_smile_adam_heat_cool.async_update.return_value
    data["da224107914542988a88561b4452b0f6"][
        "select_regulation_mode"
    ] = "cooling"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["control_state"] = "cooling"
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"][
        "cooling_state"
    ] = True
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"][
        "heating_state"
    ] = False
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.living_room")
        assert state
        assert state.state == HVACMode.COOL
        assert state.attributes["hvac_action"] == "cooling"
        assert state.attributes["hvac_modes"] == [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
        ]


async def test_adam_climate_adjust_negative_testing(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test PlugwiseError exception."""
    mock_smile_adam.set_temperature.side_effect = PlugwiseError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {"entity_id": "climate.woonkamer", "temperature": 25},
            blocking=True,
        )


async def test_adam_climate_entity_climate_changes(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test handling of user requests in adam climate device environment."""
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {"entity_id": "climate.woonkamer", "temperature": 25},
        blocking=True,
    )
    assert mock_smile_adam.set_temperature.call_count == 1
    mock_smile_adam.set_temperature.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", {"setpoint": 25.0}
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {
            "entity_id": "climate.woonkamer",
            "hvac_mode": "heat",
            "temperature": 25,
        },
        blocking=True,
    )
    assert mock_smile_adam.set_temperature.call_count == 2
    mock_smile_adam.set_temperature.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", {"setpoint": 25.0}
    )

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {"entity_id": "climate.woonkamer", "temperature": 150},
            blocking=True,
        )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_PRESET_MODE,
        {"entity_id": "climate.woonkamer", "preset_mode": "away"},
        blocking=True,
    )
    assert mock_smile_adam.set_preset.call_count == 1
    mock_smile_adam.set_preset.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", "away"
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {"entity_id": "climate.woonkamer", "hvac_mode": "heat"},
        blocking=True,
    )
    assert mock_smile_adam.set_schedule_state.call_count == 2
    mock_smile_adam.set_schedule_state.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", "off"
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {
                "entity_id": "climate.jessie",
                "hvac_mode": "dry",
            },
            blocking=True,
        )


async def test_adam_climate_off_mode_change(
    hass: HomeAssistant,
    mock_smile_adam_4: MagicMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test handling of user requests in adam climate device environment."""
    state = hass.states.get("climate.slaapkamer")
    assert state
    assert state.state == HVACMode.OFF
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            "entity_id": "climate.slaapkamer",
            "hvac_mode": "heat",
        },
        blocking=True,
    )
    assert mock_smile_adam_4.set_schedule_state.call_count == 1
    assert mock_smile_adam_4.set_regulation_mode.call_count == 1
    mock_smile_adam_4.set_regulation_mode.assert_called_with("heating")

    state = hass.states.get("climate.kinderkamer")
    assert state
    assert state.state == HVACMode.HEAT
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            "entity_id": "climate.kinderkamer",
            "hvac_mode": "off",
        },
        blocking=True,
    )
    assert mock_smile_adam_4.set_schedule_state.call_count == 1
    assert mock_smile_adam_4.set_regulation_mode.call_count == 2
    mock_smile_adam_4.set_regulation_mode.assert_called_with("off")

    state = hass.states.get("climate.logeerkamer")
    assert state
    assert state.state == HVACMode.HEAT
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            "entity_id": "climate.logeerkamer",
            "hvac_mode": "heat",
        },
        blocking=True,
    )
    assert mock_smile_adam_4.set_schedule_state.call_count == 1
    assert mock_smile_adam_4.set_regulation_mode.call_count == 2


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_anna_climate_entity_attributes(
    hass: HomeAssistant, mock_smile_anna: MagicMock, init_integration: MagicMock
) -> None:
    """Test creation of anna climate device environment."""
    state = hass.states.get("climate.anna")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "heating"
    assert state.attributes["hvac_modes"] == [
        HVACMode.AUTO,
        HVACMode.HEAT_COOL,
    ]

    assert "no_frost" in state.attributes["preset_modes"]
    assert "home" in state.attributes["preset_modes"]

    assert state.attributes["current_temperature"] == 19.3
    assert state.attributes["preset_mode"] == "home"
    assert state.attributes["supported_features"] == 18
    assert state.attributes["target_temp_high"] == 30
    assert state.attributes["target_temp_low"] == 20.5
    assert state.attributes["min_temp"] == 4
    assert state.attributes["max_temp"] == 30
    assert math.isclose(
        state.attributes["target_temp_step"], 0.1, rel_tol=1e-09, abs_tol=1e-09
    )

@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_cooling"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_anna_2_climate_entity_attributes(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test creation of anna climate device environment."""
    state = hass.states.get("climate.anna")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "cooling"
    assert state.attributes["hvac_modes"] == [
        HVACMode.AUTO,
        HVACMode.HEAT_COOL,
    ]
    assert state.attributes["supported_features"] == 18
    assert state.attributes["target_temp_high"] == 30
    assert state.attributes["target_temp_low"] == 20.5


@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_idle"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_anna_3_climate_entity_attributes(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test creation of anna climate device environment."""
    state = hass.states.get("climate.anna")
    assert state
    assert state.state == HVACMode.AUTO
    assert state.attributes["hvac_action"] == "idle"
    assert state.attributes["hvac_modes"] == [
        HVACMode.AUTO,
        HVACMode.HEAT_COOL,
    ]


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
async def test_anna_climate_entity_climate_changes(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    init_integration: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test handling of user requests in anna climate device environment."""
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {"entity_id": "climate.anna", "target_temp_high": 30, "target_temp_low": 20},
        blocking=True,
    )
    assert mock_smile_anna.set_temperature.call_count == 1
    mock_smile_anna.set_temperature.assert_called_with(
        "c784ee9fdab44e1395b8dee7d7a497d5",
        {"setpoint_high": 30.0, "setpoint_low": 20.0},
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_PRESET_MODE,
        {"entity_id": "climate.anna", "preset_mode": "away"},
        blocking=True,
    )
    assert mock_smile_anna.set_preset.call_count == 1
    mock_smile_anna.set_preset.assert_called_with(
        "c784ee9fdab44e1395b8dee7d7a497d5", "away"
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {"entity_id": "climate.anna", "hvac_mode": "auto"},
        blocking=True,
    )
    assert mock_smile_anna.set_schedule_state.call_count == 0
    # hvac_mode is already auto so not called.

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {"entity_id": "climate.anna", "hvac_mode": "heat_cool"},
        blocking=True,
    )
    assert mock_smile_anna.set_schedule_state.call_count == 1
    mock_smile_anna.set_schedule_state.assert_called_with(
        "c784ee9fdab44e1395b8dee7d7a497d5", "off"
    )

    data = mock_smile_anna.async_update.return_value
    data["3cb70739631c4d17a86b8b12e8a5161b"]["available_schedules"] = []
    data["3cb70739631c4d17a86b8b12e8a5161b"]["select_schedule"] = None
    data["3cb70739631c4d17a86b8b12e8a5161b"]["climate_mode"] = "heat_cool"
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.anna")
        assert state.state == HVACMode.HEAT_COOL
        assert state.attributes["hvac_modes"] == [HVACMode.HEAT_COOL]
