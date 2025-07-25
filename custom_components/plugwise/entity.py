"""Generic Plugwise Entity Class."""

from __future__ import annotations

from plugwise.constants import GwEntityData

from homeassistant.const import ATTR_NAME, ATTR_VIA_DEVICE, CONF_HOST
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    CONNECTION_ZIGBEE,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    AVAILABLE,
    DOMAIN,
    FIRMWARE,
    HARDWARE,
    MAC_ADDRESS,
    MODEL,
    MODEL_ID,
    VENDOR,
    ZIGBEE_MAC_ADDRESS,
)

# Upstream consts
from .coordinator import PlugwiseDataUpdateCoordinator


class PlugwiseEntity(CoordinatorEntity[PlugwiseDataUpdateCoordinator]):
    """Represent a PlugWise Entity."""

    _attr_has_entity_name = True

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

        data = coordinator.data[device_id]
        connections = set()
        if mac := data.get(MAC_ADDRESS):
            connections.add((CONNECTION_NETWORK_MAC, mac))
        if mac := data.get(ZIGBEE_MAC_ADDRESS):
            connections.add((CONNECTION_ZIGBEE, mac))

        self._attr_device_info = DeviceInfo(
            configuration_url=configuration_url,
            identifiers={(DOMAIN, device_id)},
            connections=connections,
            manufacturer=data.get(VENDOR),
            model=data.get(MODEL),
            model_id=data.get(MODEL_ID),
            name=coordinator.api.smile.name,
            sw_version=data.get(FIRMWARE),
            hw_version=data.get(HARDWARE),
        )

        if device_id != coordinator.api.gateway_id:
            self._attr_device_info.update(
                {
                    ATTR_NAME: data.get(ATTR_NAME),
                    ATTR_VIA_DEVICE: (
                        DOMAIN,
                        str(self.coordinator.api.gateway_id),
                    ),
                }
            )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            # Upstream: Do not change the AVAILABLE line below: some Plugwise devices and zones
            # Upstream: do not provide their availability-status!
            self._dev_id in self.coordinator.data
            and (AVAILABLE not in self.device or self.device[AVAILABLE] is True)
            and super().available
        )

    @property
    def device(self) -> GwEntityData:
        """Return data for this device."""
        return self.coordinator.data[self._dev_id]
