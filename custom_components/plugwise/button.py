"""Plugwise Button component for Home Assistant."""
from __future__ import annotations

"""Implement POST /core/gateways;@reboot"""



PLUGWISE_BUTTONS: Final[list[ShellyButtonDescription[Any]]] = [
    ShellyButtonDescription[ShellyBlockCoordinator | ShellyRpcCoordinator](
        key="reboot",
        name="Reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
        press_action=lambda coordinator: coordinator.device.trigger_reboot(),
    ),


 async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smile sensors from a ConfigEntry."""
    coordinator = get_coordinator(hass, entry.entry_id)

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        entities: list[PlugwiseSensorEntity] = []
        for device_id, device in coordinator.data.devices.items():
            if not (sensors := device.get(SENSORS)):
                continue
            for description in PLUGWISE_SENSORS:
                if description.key not in sensors:
                    continue
                entities.append(
                    PlugwiseSensorEntity(
                        coordinator,
                        device_id,
                        description,
                    )
                )
                LOGGER.debug(
                    "Add %s %s sensor", device[ATTR_NAME], description.translation_key or description.key
                )

        async_add_entities(entities)

    entry.async_on_unload(coordinator.async_add_listener(_add_entities))

    _add_entities()


class PlugwiseButton(..., ButtonEntity):
    """Defines a Plugwise button."""

    entity_description: PlugwiseButtonEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, device_id)
        self.entity_description = description

        self._attr_name = f"{coordinator.device.name} {description.name}"
        self._attr_unique_id = f"{coordinator.mac}_{description.key}"
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, coordinator.mac)}
        )

    async def async_press(self) -> None:
        """Triggers the Shelly button press service."""
        await self.entity_description.press_action(self.coordinator)


class PlugwiseSensorEntity(PlugwiseEntity, SensorEntity):
    """Represent Plugwise Sensors."""

    entity_description: PlugwiseSensorEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def native_value(self) -> int | float:
        """Return the value reported by the sensor."""
        return self.device[SENSORS][self.entity_description.key]   