"""Tests for the Plugwise Sensor integration."""

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_adam_climate_sensor_entities(
    hass: HomeAssistant, mock_smile_adam: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of climate related sensor entities."""
    state = hass.states.get("sensor.adam_outdoor_temperature")
    assert state
    assert float(state.state) == 7.81

    state = hass.states.get("sensor.cv_pomp_electricity_consumed")
    assert state
    assert float(state.state) == 35.6

    state = hass.states.get("sensor.onoff_water_temperature")
    assert state
    assert float(state.state) == 70.0

    state = hass.states.get("sensor.cv_pomp_electricity_consumed_interval")
    assert state
    assert float(state.state) == 7.37

    await hass.helpers.entity_component.async_update_entity(
        "sensor.zone_lisa_wk_battery"
    )

    state = hass.states.get("sensor.zone_lisa_wk_battery")
    assert state
    assert int(state.state) == 34


async def test_anna_as_smt_climate_sensor_entities(
    hass: HomeAssistant, mock_smile_anna: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of climate related sensor entities."""
    state = hass.states.get("sensor.opentherm_outdoor_air_temperature")
    assert state
    assert float(state.state) == 3.0

    state = hass.states.get("sensor.opentherm_water_temperature")
    assert state
    assert float(state.state) == 29.1

    state = hass.states.get("sensor.opentherm_dhw_temperature")
    assert state
    assert float(state.state) == 46.3

    state = hass.states.get("sensor.anna_illuminance")
    assert state
    assert float(state.state) == 86.0


async def test_anna_climate_sensor_entities(
    hass: HomeAssistant, mock_smile_anna: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of climate related sensor entities as single master thermostat."""
    state = hass.states.get("sensor.opentherm_outdoor_air_temperature")
    assert state
    assert float(state.state) == 3.0


async def test_p1_dsmr_sensor_entities(
    hass: HomeAssistant, mock_smile_p1: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of power related sensor entities."""
    state = hass.states.get("sensor.p1_net_electricity_point")
    assert state
    assert float(state.state) == -2816.0

    state = hass.states.get("sensor.p1_electricity_consumed_off_peak_cumulative")
    assert state
    assert float(state.state) == 551.09

    state = hass.states.get("sensor.p1_electricity_produced_peak_point")
    assert state
    assert float(state.state) == 2816.0

    state = hass.states.get("sensor.p1_electricity_consumed_peak_cumulative")
    assert state
    assert float(state.state) == 442.932

    state = hass.states.get("sensor.p1_gas_consumed_cumulative")
    assert state
    assert float(state.state) == 584.85


async def test_stretch_sensor_entities(
    hass: HomeAssistant, mock_stretch: MagicMock, init_integration: MockConfigEntry
) -> None:
    """Test creation of power related sensor entities."""
    state = hass.states.get("sensor.boiler_1EB31_electricity_consumed")
    assert state
    assert float(state.state) == 1.19

    state = hass.states.get("sensor.droger_52559_electricity_consumed_interval")
    assert state
    assert float(state.state) == 0.0
