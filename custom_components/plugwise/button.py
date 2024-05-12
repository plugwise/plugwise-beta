"""Plugwise Button component for Home Assistant."""
from __future__ import annotations

from plugwise import Smile

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import GATEWAY_ID, LOGGER
from .coordinator import PlugwiseDataUpdateCoordinator
from .entity import get_coordinator


BUTTON_TYPES: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="reboot",
        translation_key="reboot"
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    )
)


 async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Plugwise buttons from a ConfigEntry."""
    coordinator = get_coordinator(hass, entry.entry_id)

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseButtonEntity] = []
        for device_id, device in coordinator.data.devices.items():
            if device_id == coordinator.data.gateway[GATEWAY_ID]:
                for description in BUTTON_TYPES:
                    entities.append(
                        PlugwiseButtonEntity(
                            coordinator,
                            device_id,
                            description,
                        )
                )
                LOGGER.debug(
                    "Add %s %s button", device[ATTR_NAME], description.key
                )

        async_add_entities(entities)

    entry.async_on_unload(coordinator.async_add_listener(_add_entities))

    _add_entities()


class PlugwiseButton(ButtonEntity):
    """Defines a Plugwise button."""

    entity_description: ButtonEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, device_id)
        self.device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"

    @plugwise_command
    async def async_press(self) -> None:
        """Triggers the Shelly button press service."""
        await self.coordinator.api.reboot_gateway()
