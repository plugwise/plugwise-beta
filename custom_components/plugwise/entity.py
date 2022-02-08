"""Generic Plugwise Entity Classes."""
from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PlugwiseData, PlugwiseDataUpdateCoordinator


class PlugwiseGatewayEntity(CoordinatorEntity[PlugwiseData]):
    """Represent a PlugWise Smile or Stretch Entity."""

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        description: PlugwiseEntityDescription,
        device_id: str,
    ) -> None:
        """Initialise the gateway."""
        super().__init__(coordinator)

        configuration_url: str | None = None
        if entry := self.coordinator.config_entry:
            configuration_url = f"http://{entry.data[CONF_HOST]}"

        data = self.coordinator.data.devices[device_id]
        self._attr_available = super().available
        self._attr_device_class = description.device_class
        self._attr_device_info = DeviceInfo(
            configuration_url=configuration_url,
            identifiers={(DOMAIN, device_id)},
            manufacturer=data.get("vendor"),
            model=data.get("model"),
            name=f"Smile {coordinator.data.gateway['smile_name']}",
            sw_version=fw,
        )
        self.entity_description = description

        if device_id != coordinator.data.gateway["gateway_id"]:
            self._attr_device_info.update(
                name=data.get("name"),
                via_device=(DOMAIN, str(coordinator.data.gateway["gateway_id"])),
            )
