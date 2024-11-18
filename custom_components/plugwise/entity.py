"""Generic Plugwise Entity Class."""

from __future__ import annotations

from plugwise.constants import DeviceZoneData

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
    GATEWAY_ID,
    HARDWARE,
    MAC_ADDRESS,
    MODEL,
    MODEL_ID,
    SMILE_NAME,
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

        if (data := coordinator.data.devices.get(device_id)) is not None:
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
                name=coordinator.data.gateway[SMILE_NAME],
                sw_version=data.get(FIRMWARE),
                hw_version=data.get(HARDWARE),
            )

            if device_id != coordinator.data.gateway[GATEWAY_ID]:
                self._attr_device_info.update(
                    {
                        ATTR_NAME: data.get(ATTR_NAME),
                        ATTR_VIA_DEVICE: (
                            DOMAIN,
                            str(self.coordinator.data.gateway[GATEWAY_ID]),
                        ),
                    }
                )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            # Upstream: Do not change the AVAILABLE line below: some Plugwise devices
            # Upstream: do not provide their availability-status!
            self._dev_id in self.coordinator.data.devices
            and (AVAILABLE not in self.device_or_zone or self.device_or_zone[AVAILABLE] is True)
            and super().available
        )

    @property
    def device_or_zone(self) -> DeviceZoneData:
        """Return the device or zone connected to the dev_id."""
        if (device := self.coordinator.data.devices.get(self._dev_id)) is not None:
            return device

        return self.coordinator.data.zones[self._dev_id]

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self._handle_coordinator_update()
        await super().async_added_to_hass()
