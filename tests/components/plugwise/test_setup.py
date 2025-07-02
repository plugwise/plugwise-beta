"""Tests for the Plugwise Climate integration."""


import logging  # For potential debugging

import pytest
from syrupy.assertion import SnapshotAssertion

from tests.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
import homeassistant.helpers.entity_registry as er

_LOGGER = logging.getLogger(__name__) # For logging


@pytest.mark.parametrize(
    "mock_config_entry, chosen_env, cooling_present",
    [
        pytest.param("mock_smile_anna", "anna_heatpump_heating", True, id="Anna Thermostat"),
        pytest.param("mock_smile_adam", "adam_multiple_devices_per_zone", True, id="Adam Gateway"),
#        pytest.param("mock_stretch", "", id="Stretch Gateway"),
    ],
    indirect=["mock_config_entry", "chosen_env", "cooling_present"]  
)
async def test_plugwise_full_registry_snapshot(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    request: pytest.FixtureRequest,
    mock_config_entry: MockConfigEntry,
    chosen_env: str,
    cooling_present: bool
) -> None:
    """Test that all config_entry_mock entities and devices are correctly registered via snapshot."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    _LOGGER.debug("Testing with config entry mock: %s (Environment: %s, Cooling: %s)",
                  mock_config_entry.title, chosen_env, cooling_present)

    assert mock_config_entry.state is ConfigEntryState.LOADED

    # Determine base name for the snapshot based on the fixture_name
    clean_name_part = mock_config_entry.domain # Or mock_config_entry.title.lower().replace(" ", "_")
    snapshot_base_name = f"{clean_name_part}_{chosen_env}"
    if cooling_present:
        snapshot_base_name += "_cooling"


    entity_registry = er.async_get(hass)
    plugwise_entities = {}
    for entry in entity_registry.entities.values():
        if entry.config_entry_id == mock_config_entry.entry_id:
            plugwise_entities[entry.entity_id] = {
                "platform": entry.platform,
                "unique_id": entry.unique_id,
                "device_id": entry.device_id,
                "original_name": entry.original_name,
                "original_device_class": entry.original_device_class,
                "original_unit_of_measurement": entry.original_unit_of_measurement,
                "domain": entry.domain,
                "disabled_by": entry.disabled_by,
                "hidden_by": entry.hidden_by,
                "capabilities": entry.capabilities,
                "supported_features": entry.supported_features,
            }

    # Sort the dictionary by entity_id for consistent snapshot order
    assert dict(sorted(plugwise_entities.items())) == snapshot(name=f"{snapshot_base_name}_entity_registry")


    device_registry = dr.async_get(hass)
    plugwise_devices = {}
    for device_entry in device_registry.devices.values():
        if mock_config_entry.entry_id in device_entry.config_entries:
            plugwise_devices[device_entry.id] = {
                "name": device_entry.name,
                "model": device_entry.model,
                "manufacturer": device_entry.manufacturer,
                "sw_version": device_entry.sw_version,
                "hw_version": device_entry.hw_version,
                "via_device_id": device_entry.via_device_id,
                "identifiers": sorted([list(i) for i in device_entry.identifiers]), # Sort nested lists
                "connections": sorted([list(c) for c in device_entry.connections]), # Sort nested lists
                "suggested_area": device_entry.suggested_area,
            }

    # Sort the dictionary by device ID for consistent snapshot order
    assert dict(sorted(plugwise_devices.items())) == snapshot(name=f"{snapshot_base_name}_device_registry")
