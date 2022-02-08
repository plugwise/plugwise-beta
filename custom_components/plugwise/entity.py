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
        model: str,
        name: str,
        vendor: str,
        fw: str,
    ) -> None:
        """Initialise the gateway."""
        super().__init__(coordinator)

        entry = coordinator.config_entry
        gateway_id = coordinator.data.gateway["gateway_id"]
        self._attr_available = super().available
        self._attr_device_class = description.device_class
        self._attr_device_info = DeviceInfo(
            configuration_url=f"http://{entry.data[CONF_HOST]}",
            identifiers={(DOMAIN, device_id)},
            manufacturer=vendor,
            model=model,
            name=f"Smile {coordinator.data.gateway['smile_name']}",
            sw_version=fw,
        )
        self.entity_description = description

        if device_id != gateway_id:
            self._attr_device_info.update(
                name=name,
                via_device=(DOMAIN, gateway_id),
            )
