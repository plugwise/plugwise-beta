"""Generic Plugwise Entity Class."""
from __future__ import annotations

from typing import Any

from homeassistant.const import ATTR_NAME, ATTR_VIA_DEVICE, CONF_HOST
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    CONNECTION_ZIGBEE,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PlugwiseData, PlugwiseDataUpdateCoordinator


class PlugwiseEntity(CoordinatorEntity[PlugwiseData]):
    """Represent a PlugWise Entity."""

    coordinator: PlugwiseDataUpdateCoordinator

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialise the gateway."""
        super().__init__(coordinator)
        self._dev_id = device_id

        configuration_url: str | None = None
        if entry := self.coordinator.config_entry:
            configuration_url = f"http://{entry.data[CONF_HOST]}"

        data = coordinator.data.devices[device_id]
        connections = set()
        if mac := data.get("mac_address"):
            connections.add((CONNECTION_NETWORK_MAC, mac))
        if mac := data.get("zigbee_mac_address"):
            connections.add((CONNECTION_ZIGBEE, mac))

        self._attr_device_info = DeviceInfo(
            configuration_url=configuration_url,
            identifiers={(DOMAIN, device_id)},
            connections=connections,
            manufacturer=data.get("vendor"),
            model=data.get("model"),
            name=f"Smile {coordinator.data.gateway['smile_name']}",
            sw_version=data.get("fw"),
            hw_version=data.get("hw"),
        )

        if device_id != coordinator.data.gateway["gateway_id"]:
            self._attr_device_info.update(
                {
                    ATTR_NAME: data.get("name"),
                    ATTR_VIA_DEVICE: (
                        DOMAIN,
                        str(self.coordinator.data.gateway["gateway_id"]),
                    ),
                }
            )
    
    async def async_send_api_call(self, target: str, command: str) -> bool:
        """Send api call."""
        result = False
        if command == "set_max_boiler_temperature":
            result = await self.coordinator.api.set_max_boiler_temperature(target)
        if command == "set_regulation_mode":
            result = await self.coordinator.api.set_regulation_mode(target)
        if command == "set_schedule_state":
            result = await self.coordinator.api.set_schedule_state(
                self.device.get("location"),
                target,
                SCHEDULE_ON,
            )

        return result

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self._dev_id in self.coordinator.data.devices

    @property
    def device(self) -> dict[str, Any]:
        """Return data for this device."""
        return self.coordinator.data.devices[self._dev_id]

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self._handle_coordinator_update()
        await super().async_added_to_hass()
