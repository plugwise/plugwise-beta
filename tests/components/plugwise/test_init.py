"""Tests for the Plugwise Climate integration."""
from datetime import timedelta
import logging
from unittest.mock import MagicMock, patch

from plugwise.exceptions import (
    ConnectionFailedError,
    InvalidAuthentication,
    InvalidXMLError,
    PlugwiseError,
    ResponseError,
    UnsupportedDeviceError,
)
import pytest

from freezegun.api import FrozenDateTimeFactory
from homeassistant.components.plugwise.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, async_fire_time_changed

LOGGER = logging.getLogger(__package__)

HA_PLUGWISE_SMILE_ASYNC_UPDATE = (
    "homeassistant.components.plugwise.coordinator.Smile.async_update"
)
HEATER_ID = "1cbf783bb11e4a7c8a6843dee3a86927"  # Opentherm device_id for migration
PLUG_ID = "cd0ddb54ef694e11ac18ed1cbce5dbbd"  # VCR device_id for migration
SECONDARY_ID = (
    "1cbf783bb11e4a7c8a6843dee3a86927"  # Heater_central device_id for migration
)
TOM = {
    "01234567890abcdefghijklmnopqrstu": {
        "available": True,
        "dev_class": "thermo_sensor",
        "firmware": "2020-11-04T01:00:00+01:00",
        "hardware": "1",
        "location": "f871b8c4d63549319221e294e4f88074",
        "model": "Tom/Floor",
        "name": "Tom Zolder",
        "binary_sensors": {
            "low_battery": False,
        },
        "sensors": {
            "battery": 99,
            "temperature": 18.6,
            "temperature_difference": 2.3,
            "valve_position": 0.0,
        },
        "temperature_offset": {
            "lower_bound": -2.0,
            "resolution": 0.1,
            "setpoint": 0.1,
            "upper_bound": 2.0,
        },
        "vendor": "Plugwise",
        "zigbee_mac_address": "ABCD012345670A01",
    },
}


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
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


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
@pytest.mark.parametrize(
    ("side_effect", "entry_state"),
    [
        (ConnectionFailedError, ConfigEntryState.SETUP_RETRY),
        (InvalidAuthentication, ConfigEntryState.SETUP_ERROR),
        (InvalidXMLError, ConfigEntryState.SETUP_RETRY),
        (ResponseError, ConfigEntryState.SETUP_RETRY),
        (PlugwiseError, ConfigEntryState.SETUP_RETRY),
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


@pytest.mark.parametrize("chosen_env", ["p1v4_442_single"], indirect=True)
@pytest.mark.parametrize("gateway_id", ["a455b61e52394b2db5081ce025a430f3"], indirect=True)
async def test_device_in_dr(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_p1: MagicMock,
    device_registry: dr.DeviceRegistry,
) -> None:
    """Test Gateway device registry data."""
    mock_config_entry.add_to_hass(hass)
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    device_entry = device_registry.async_get_device(
        identifiers={(DOMAIN, "a455b61e52394b2db5081ce025a430f3")}
    )
    assert device_entry.hw_version == "AME Smile 2.0 board"
    assert device_entry.manufacturer == "Plugwise"
    assert device_entry.model == "Gateway"
    assert device_entry.model_id == "smile"
    assert device_entry.name == "Smile P1"
    assert device_entry.sw_version == "4.4.2"


async def check_migration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    entitydata: dict,
    old_unique_id: str,
    new_unique_id: str,
) -> None:
    """Helper-function for checking a unique_id migration."""
    mock_config_entry.add_to_hass(hass)

    entity_registry = er.async_get(hass)
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


@pytest.mark.parametrize("chosen_env", ["anna_heatpump_heating"], indirect=True)
@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": Platform.SENSOR,
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
    entitydata: dict,
    old_unique_id: str,
    new_unique_id: str,
    mock_smile_anna: MagicMock,
) -> None:
    """Test migration of unique_id."""
    await check_migration(
        hass, mock_config_entry, entitydata, old_unique_id, new_unique_id
    )


@pytest.mark.parametrize(
    ("entitydata", "old_unique_id", "new_unique_id"),
    [
        (
            {
                "domain": Platform.BINARY_SENSOR,
                "platform": DOMAIN,
                "unique_id": f"{SECONDARY_ID}-slave_boiler_state",
                "suggested_object_id": f"{SECONDARY_ID}-slave_boiler_state",
                "disabled_by": None,
            },
            f"{SECONDARY_ID}-slave_boiler_state",
            f"{SECONDARY_ID}-secondary_boiler_state",
        ),
        (
            {
                "domain": Platform.SWITCH,
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
    entitydata: dict,
    old_unique_id: str,
    new_unique_id: str,
    mock_smile_adam: MagicMock,
) -> None:
    """Test migration of unique_id."""
    await check_migration(
        hass, mock_config_entry, entitydata, old_unique_id, new_unique_id
    )

#### pw-beta only ####
@pytest.mark.parametrize("chosen_env", ["m_anna_heatpump_cooling"], indirect=True)
async def test_entry_migration(
    hass: HomeAssistant, mock_smile_anna: MagicMock
) -> None:
    """Test config entry 1.2 -> 1.1 migration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "127.0.0.1",
            CONF_MAC: "AA:BB:CC:DD:EE:FF",
            CONF_PASSWORD: "test-password",
            CONF_PORT: 80,
            CONF_TIMEOUT: 30,
            CONF_USERNAME: "smile",
        },
        minor_version=2,
        version=1,
        unique_id="smile98765",
    )

    entry.runtime_data = MagicMock(api=mock_smile_anna)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.version == 1
    assert entry.minor_version == 1
    assert entry.data.get(CONF_TIMEOUT) is None
    assert entry.state is ConfigEntryState.LOADED


@pytest.mark.parametrize("chosen_env", ["m_adam_heating"], indirect=True)
async def test_update_device(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_smile_adam_heat_cool: MagicMock,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test a clean-up of the device_registry."""
    data = mock_smile_adam_heat_cool.async_update.return_value

    mock_config_entry.add_to_hass(hass)
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    assert (
        len(er.async_entries_for_config_entry(entity_registry, mock_config_entry.entry_id))
        == 35
    )
    assert (
        len(dr.async_entries_for_config_entry(device_registry, mock_config_entry.entry_id))
        == 6
    )

    # Add a 2nd Tom/Floor
    data.devices.update(TOM)
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        assert (
            len(er.async_entries_for_config_entry(entity_registry, mock_config_entry.entry_id))
            == 41
        )
        assert (
            len(dr.async_entries_for_config_entry(device_registry, mock_config_entry.entry_id))
            == 7
        )
        item_list: list[str] = []
        for device_entry in list(device_registry.devices.values()):
            item_list.extend(x[1] for x in device_entry.identifiers)
        assert "01234567890abcdefghijklmnopqrstu" in item_list

    # Remove the existing Tom/Floor
    data.devices.pop("1772a4ea304041adb83f357b751341ff")
    with patch(HA_PLUGWISE_SMILE_ASYNC_UPDATE, return_value=data):
        freezer.tick(timedelta(minutes=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

        assert (
            len(er.async_entries_for_config_entry(entity_registry, mock_config_entry.entry_id))
            == 35
        )
        assert (
            len(dr.async_entries_for_config_entry(device_registry, mock_config_entry.entry_id))
            == 6
        )
        item_list: list[str] = []
        for device_entry in list(device_registry.devices.values()):
            item_list.extend(x[1] for x in device_entry.identifiers)
        assert "1772a4ea304041adb83f357b751341ff" not in item_list
