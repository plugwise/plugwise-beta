"""Tests for the Plugwise Climate integration."""
import logging
from unittest.mock import MagicMock

from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidXMLError,
    ResponseError,
    UnsupportedDeviceError,
)
import pytest

from homeassistant.components.plugwise.const import DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get

from tests.common import MockConfigEntry

LOGGER = logging.getLogger(__package__)

HEATER_ID = "1cbf783bb11e4a7c8a6843dee3a86927"  # Opentherm device_id for migration
PLUG_ID = "cd0ddb54ef694e11ac18ed1cbce5dbbd"  # VCR device_id for migration


async def test_load_unload_config_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_anna: MagicMock,
) -> None:
    """Test the Plugwise configuration entry loading/unloading."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert len(mock_smile_anna.connect.mock_calls) == 1

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.data.get(DOMAIN)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize(
    ("side_effect", "entry_state"),
    [
        (ConnectionFailedError, ConfigEntryState.SETUP_RETRY),
        (InvalidAuthentication, ConfigEntryState.SETUP_ERROR),
        (InvalidXMLError, ConfigEntryState.SETUP_RETRY),
        (ResponseError, ConfigEntryState.SETUP_RETRY),
        (UnsupportedDeviceError, ConfigEntryState.SETUP_ERROR),
    ],
)
async def test_gateway_config_entry_not_ready(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_anna: MagicMock,
    side_effect: Exception,
    entry_state: ConfigEntryState,
) -> None:
    """Test the Plugwise configuration entry not ready."""
    mock_smile_anna.async_update.side_effect = side_effect

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert len(mock_smile_anna.connect.mock_calls) == 1
    assert mock_config_entry.state is entry_state


@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": SENSOR_DOMAIN,
                "platform": DOMAIN,
                "unique_id": f"{HEATER_ID}-outdoor_temperature",
                "suggested_object_id": f"{HEATER_ID}-outdoor_temperature",
                "disabled_by": None,
            },
            f"{HEATER_ID}-outdoor_temperature",
            f"{HEATER_ID}-outdoor_air_temperature",
        ),
    ],
)
async def test_migrate_unique_id_temperature(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_anna: MagicMock,
    entitydata: dict,
    old_unique_id: str,
    new_unique_id: str,
) -> None:
    """Test migration of unique_id."""
    mock_config_entry.add_to_hass(hass)

    entity_registry = async_get(hass)
    entity: entity_registry.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=mock_config_entry,
    )
    assert entity.unique_id == old_unique_id
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == new_unique_id


@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": SWITCH_DOMAIN,
                "platform": DOMAIN,
                "unique_id": f"{PLUG_ID}-plug",
                "suggested_object_id": f"{PLUG_ID}-plug",
                "disabled_by": None,
            },
            f"{PLUG_ID}-plug",
            f"{PLUG_ID}-relay",
        ),
    ],
)
async def test_migrate_unique_id_relay(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_adam: MagicMock,
    entitydata: dict,
    old_unique_id: str,
    new_unique_id: str,
) -> None:
    """Test migration of unique_id."""
    mock_config_entry.add_to_hass(hass)

    entity_registry = async_get(hass)
    entity: entity_registry.RegistryEntry = entity_registry.async_get_or_create(
        **entitydata,
        config_entry=mock_config_entry,
    )
    assert entity.unique_id == old_unique_id
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_migrated = entity_registry.async_get(entity.entity_id)
    assert entity_migrated
    assert entity_migrated.unique_id == new_unique_id


@pytest.mark.parametrize(
    ("entitydata"),
    [
        {
            "domain": SENSOR_DOMAIN,
            "platform": DOMAIN,
            "unique_id": f"{HEATER_ID}-indoor_temperature",
            "suggested_object_id": "opentherm_indoor_temperature",
            "disabled_by": None,
        },
    ],
)
async def test_entity_registry_cleanup(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_anna: MagicMock,
    entitydata: dict,
) -> None:
    """Test a clean-up of the entity_registry."""
    mock_config_entry.add_to_hass(hass)

    entity_registry = async_get(hass)
    entity_registry.async_get_or_create(
        **entitydata,
        config_entry=mock_config_entry,
    )
    assert len(entity_registry.entities) == 1

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert len(entity_registry.entities) == 26

async def test_device_removal(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_adam_2: MagicMock,
) -> None:
    """Test a clean-up of the device_registry."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # dev_reg = dr.async_get(hass)
    # devices = dr.async_entries_for_config_entry(dev_reg, mock_config_entry.entry_id)
    # assert len(devices) == 3
    # assert devices[0].identifiers == {(DOMAIN, "015ae9ea3f964e668e490fa39da3870b")}
    # assert devices[0].name == "Smile Anna"