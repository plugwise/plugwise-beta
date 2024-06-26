"""Plugwise Button component for Home Assistant."""
from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.const import ATTR_NAME, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PlugwiseConfigEntry
from .const import GATEWAY_ID, LOGGER, REBOOT
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Plugwise buttons from a ConfigEntry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities during init and runtime."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseButtonEntity] = []
        gateway = coordinator.data.gateway
        for device_id in coordinator.new_devices:
            device = coordinator.data.devices[device_id]
            if device_id == gateway[GATEWAY_ID] and REBOOT in gateway:
                entities.append(PlugwiseButtonEntity(coordinator, device_id))
                LOGGER.debug("Add %s reboot button", device[ATTR_NAME])

        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseButtonEntity(PlugwiseEntity, ButtonEntity):
    """Defines a Plugwise button."""

    _attr_device_class: ButtonDeviceClass.RESTART

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, device_id)
        self.device_id = device_id
        self._attr_unique_id = f"{device_id}-reboot"

    @plugwise_command
    async def async_press(self) -> None:
        """Triggers the Plugwise button press service."""
        await self.coordinator.api.reboot_gateway()
