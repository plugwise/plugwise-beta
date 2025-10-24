"""Tests for the Plugwise Climate integration."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from plugwise.exceptions import PlugwiseError
import pytest

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.climate import (
    ATTR_HVAC_ACTION,
    ATTR_HVAC_MODE,
    ATTR_HVAC_MODES,
    ATTR_PRESET_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    DOMAIN as CLIMATE_DOMAIN,
    PRESET_AWAY,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
    HVACAction,
    HVACMode,
)
from homeassistant.components.plugwise.climate import PlugwiseClimateExtraStoredData
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion

from tests.common import (
    MockConfigEntry,
    async_fire_time_changed,
    mock_restore_cache_with_extra_data,
    snapshot_platform,
)

HA_PLUGWISE_SMILE_ASYNC_UPDATE = (
    "homeassistant.components.plugwise.coordinator.Smile.async_update"
)


@pytest.mark.parametrize("platforms", [(CLIMATE_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_adam_climate_snapshot(
    hass: HomeAssistant,
    mock_smile_adam: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Adam climate snapshot."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


async def test_adam_climate_entity_climate_changes(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test handling of user requests in adam climate device environment."""
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_TEMPERATURE,
        {ATTR_ENTITY_ID: "climate.woonkamer", ATTR_TEMPERATURE: 25},
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
            ATTR_ENTITY_ID: "climate.woonkamer",
            ATTR_HVAC_MODE: HVACMode.HEAT,
            ATTR_TEMPERATURE: 25,
        },
        blocking=True,
    )
    assert mock_smile_adam.set_temperature.call_count == 2
    mock_smile_adam.set_temperature.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", {"setpoint": 25.0}
    )

    with pytest.raises(ServiceValidationError, match="Accepted range"):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {ATTR_ENTITY_ID: "climate.woonkamer", ATTR_TEMPERATURE: 150},
            blocking=True,
        )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_PRESET_MODE,
        {ATTR_ENTITY_ID: "climate.woonkamer", ATTR_PRESET_MODE: PRESET_AWAY},
        blocking=True,
    )
    assert mock_smile_adam.set_preset.call_count == 1
    mock_smile_adam.set_preset.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", PRESET_AWAY
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: "climate.woonkamer", ATTR_HVAC_MODE: HVACMode.HEAT},
        blocking=True,
    )
    assert mock_smile_adam.set_schedule_state.call_count == 2
    mock_smile_adam.set_schedule_state.assert_called_with(
        "c50f167537524366a5af7aa3942feb1e", STATE_OFF, "GF7  Woonkamer",
    )

    with pytest.raises(
        ServiceValidationError,
        match="HVAC mode dry is not valid. Valid HVAC modes are: auto, heat",
    ):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {
                ATTR_ENTITY_ID: "climate.jessie",
                ATTR_HVAC_MODE: HVACMode.DRY,
            },
            blocking=True,
        )

async def test_adam_climate_adjust_negative_testing(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test PlugwiseError exception."""
    mock_smile_adam.set_temperature.side_effect = PlugwiseError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {ATTR_ENTITY_ID: "climate.woonkamer", ATTR_TEMPERATURE: 25},
            blocking=True,
        )


@pytest.mark.parametrize("chosen_env", ["m_adam_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [False], indirect=True)
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_adam_restore_state_climate(
    hass: HomeAssistant,
    mock_smile_adam_heat_cool: MagicMock,
    mock_config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test restore_state for climate with restored schedule."""
    mock_restore_cache_with_extra_data(
        hass,
        [
            (
                State("climate.living_room", "heat"),
                PlugwiseClimateExtraStoredData(
                    last_active_schedule=None,
                    previous_action_mode="heating",
                ).as_dict(),
            ),
            (
                State("climate.bathroom", "heat"),
                PlugwiseClimateExtraStoredData(
                    last_active_schedule="Badkamer",
                    previous_action_mode=None,
                ).as_dict(),
            ),
        ],
    )

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert (state := hass.states.get("climate.living_room"))
    assert state.state == "heat"

    # Verify a HomeAssistantError is raised setting a schedule with last_active_schedule = None
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: "climate.living_room", ATTR_HVAC_MODE: HVACMode.AUTO},
            blocking=True,
        )

    data = mock_smile_adam_heat_cool.async_update.return_value
    data["f2bf9048bef64cc5b6d5110154e33c81"]["climate_mode"] = "off"
    data["da224107914542988a88561b4452b0f6"]["selec_regulation_mode"] = "off"
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        assert (state := hass.states.get("climate.living_room"))
        assert state.state == "off"

        # Verify restoration of previous_action_mode = heating
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: "climate.living_room", ATTR_HVAC_MODE: HVACMode.HEAT},
            blocking=True,
        )
        # Verify set_schedule_state was called with the restored schedule
        mock_smile_adam_heat_cool.set_regulation_mode.assert_called_with(
            "heating",
        )

    data = mock_smile_adam_heat_cool.async_update.return_value
    data["f871b8c4d63549319221e294e4f88074"]["climate_mode"] = "heat"
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        assert (state := hass.states.get("climate.bathroom"))
        assert state.state == "heat"

        # Verify restoration is used when setting a schedule
        await hass.services.async_call(
            CLIMATE_DOMAIN,
            SERVICE_SET_HVAC_MODE,
            {ATTR_ENTITY_ID: "climate.bathroom", ATTR_HVAC_MODE: HVACMode.AUTO},
            blocking=True,
        )
        # Verify set_schedule_state was called with the restored schedule
        mock_smile_adam_heat_cool.set_schedule_state.assert_called_with(
            "f871b8c4d63549319221e294e4f88074", STATE_ON, "Badkamer"
        )


@pytest.mark.parametrize("chosen_env", ["m_adam_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [False], indirect=True)
@pytest.mark.parametrize("platforms", [(CLIMATE_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_adam_2_climate_snapshot(
    hass: HomeAssistant,
    mock_smile_adam_heat_cool: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Adam 2 climate snapshot."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


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
    assert state.attributes[ATTR_HVAC_ACTION] == HVACAction.COOLING
    assert state.attributes[ATTR_HVAC_MODES] == [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.COOL,
    ]
    data = mock_smile_adam_heat_cool.async_update.return_value
    data["da224107914542988a88561b4452b0f6"]["select_regulation_mode"] = "heating"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["climate_mode"] = "heat"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["control_state"] = HVACAction.HEATING
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"]["cooling_state"] = False
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"]["heating_state"] = True
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.living_room")
        assert state
        assert state.state == HVACMode.HEAT
        assert state.attributes[ATTR_HVAC_ACTION] == HVACAction.HEATING
        assert state.attributes[ATTR_HVAC_MODES] == [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.HEAT,
        ]

    data = mock_smile_adam_heat_cool.async_update.return_value
    data["da224107914542988a88561b4452b0f6"]["select_regulation_mode"] = "cooling"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["climate_mode"] = "cool"
    data["f2bf9048bef64cc5b6d5110154e33c81"]["control_state"] = HVACAction.COOLING
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"]["cooling_state"] = True
    data["056ee145a816487eaa69243c3280f8bf"]["binary_sensors"]["heating_state"] = False
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.living_room")
        assert state
        assert state.state == HVACMode.COOL
        assert state.attributes[ATTR_HVAC_ACTION] == HVACAction.COOLING
        assert state.attributes[ATTR_HVAC_MODES] == [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
        ]


async def test_adam_climate_off_mode_change(
    hass: HomeAssistant,
    mock_smile_adam_jip: MagicMock,
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
            ATTR_ENTITY_ID: "climate.slaapkamer",
            ATTR_HVAC_MODE: HVACMode.HEAT,
        },
        blocking=True,
    )
    assert mock_smile_adam_jip.set_schedule_state.call_count == 1
    assert mock_smile_adam_jip.set_regulation_mode.call_count == 1
    mock_smile_adam_jip.set_regulation_mode.assert_called_with("heating")

    state = hass.states.get("climate.kinderkamer")
    assert state
    assert state.state == HVACMode.HEAT
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            ATTR_ENTITY_ID: "climate.kinderkamer",
            ATTR_HVAC_MODE: HVACMode.OFF,
        },
        blocking=True,
    )
    assert mock_smile_adam_jip.set_schedule_state.call_count == 1
    assert mock_smile_adam_jip.set_regulation_mode.call_count == 2
    mock_smile_adam_jip.set_regulation_mode.assert_called_with("off")

    state = hass.states.get("climate.logeerkamer")
    assert state
    assert state.state == HVACMode.HEAT
    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {
            ATTR_ENTITY_ID: "climate.logeerkamer",
            ATTR_HVAC_MODE: HVACMode.HEAT,
        },
        blocking=True,
    )
    assert mock_smile_adam_jip.set_schedule_state.call_count == 1
    assert mock_smile_adam_jip.set_regulation_mode.call_count == 2


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
@pytest.mark.parametrize("platforms", [(CLIMATE_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_anna_climate_snapshot(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Anna climate snapshot."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


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
        {
            ATTR_ENTITY_ID: "climate.living_room",
            ATTR_TARGET_TEMP_HIGH: 30,
            ATTR_TARGET_TEMP_LOW: 20,
        },
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
        {ATTR_ENTITY_ID: "climate.living_room", ATTR_PRESET_MODE: PRESET_AWAY},
        blocking=True,
    )
    assert mock_smile_anna.set_preset.call_count == 1
    mock_smile_anna.set_preset.assert_called_with(
        "c784ee9fdab44e1395b8dee7d7a497d5", PRESET_AWAY
    )

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: "climate.living_room", ATTR_HVAC_MODE: HVACMode.AUTO},
        blocking=True,
    )
    # hvac_mode is already auto so not called.
    assert mock_smile_anna.set_schedule_state.call_count == 0

    await hass.services.async_call(
        CLIMATE_DOMAIN,
        SERVICE_SET_HVAC_MODE,
        {ATTR_ENTITY_ID: "climate.living_room", ATTR_HVAC_MODE: HVACMode.HEAT_COOL},
        blocking=True,
    )
    assert mock_smile_anna.set_schedule_state.call_count == 1
    mock_smile_anna.set_schedule_state.assert_called_with(
        "c784ee9fdab44e1395b8dee7d7a497d5", STATE_OFF, "standaard",
    )

    # Mock user deleting last schedule from app or browser
    data = mock_smile_anna.async_update.return_value
    data["c784ee9fdab44e1395b8dee7d7a497d5"]["available_schedules"] = []
    data["c784ee9fdab44e1395b8dee7d7a497d5"]["select_schedule"] = None
    data["c784ee9fdab44e1395b8dee7d7a497d5"]["climate_mode"] = "heat_cool"
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        state = hass.states.get("climate.living_room")
        assert state.state == HVACMode.HEAT_COOL
        assert state.attributes[ATTR_HVAC_MODES] == [HVACMode.HEAT_COOL]


@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_cooling"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
@pytest.mark.parametrize("platforms", [(CLIMATE_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_anna_2_climate_snapshot(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Anna 2 climate snapshot."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)


@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_idle"], indirect=True)
@pytest.mark.parametrize("cooling_present", [True], indirect=True)
@pytest.mark.parametrize("platforms", [(CLIMATE_DOMAIN,)])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_anna_3_climate_snapshot(
    hass: HomeAssistant,
    mock_smile_anna: MagicMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    setup_platform: MockConfigEntry,
) -> None:
    """Test Anna 3 climate snapshot."""
    await snapshot_platform(hass, entity_registry, snapshot, setup_platform.entry_id)
