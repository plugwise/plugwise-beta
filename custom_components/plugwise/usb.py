"""Support for Plugwise devices connected to a Plugwise USB-stick."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity

from plugwise.constants import USB as USB_ID
from plugwise.exceptions import (
    CirclePlusError,
    NetworkDown,
    PortError,
    StickInitError,
    TimeoutException,
)
from plugwise.nodes import PlugwiseNode
from plugwise.stick import Stick

from .const import (
    ATTR_MAC_ADDRESS,
    CB_JOIN_REQUEST,
    CONF_USB_PATH,
    DOMAIN,
    PLATFORMS_USB,
    PW_TYPE,
    SERVICE_USB_DEVICE_ADD,
    SERVICE_USB_DEVICE_REMOVE,
    SERVICE_USB_DEVICE_SCHEMA,
    STICK,
    UNDO_UPDATE_LISTENER,
    USB,
)
from .models import PlugwiseEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry_usb(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Establish connection with plugwise USB-stick."""
    hass.data.setdefault(DOMAIN, {})
    device_registry = await dr.async_get_registry(hass)

    def discover_finished():
        """Create entities for all discovered nodes."""
        _LOGGER.debug(
            "Successfully discovered %s out of %s registered nodes",
            str(len(api_stick.devices)),
            str(api_stick.joined_nodes),
        )
        for component in PLATFORMS_USB:
            hass.data[DOMAIN][config_entry.entry_id][component] = []

        for mac, pw_device in api_stick.devices.items():
            # Skip unsupported devices
            if pw_device is not None:
                if USB_ID.relay in pw_device.features:
                    hass.data[DOMAIN][config_entry.entry_id][Platform.SWITCH].append(
                        mac
                    )
                if USB_ID.motion in pw_device.features:
                    hass.data[DOMAIN][config_entry.entry_id][
                        Platform.BINARY_SENSOR
                    ].append(mac)
                if (
                    USB_ID.interval_cons in pw_device.features
                    or USB_ID.interval_prod in pw_device.features
                ):
                    hass.data[DOMAIN][config_entry.entry_id][Platform.NUMBER].append(
                        mac
                    )

                hass.data[DOMAIN][config_entry.entry_id][Platform.SENSOR].append(mac)

        hass.config_entries.async_setup_platforms(config_entry, PLATFORMS_USB)

        def add_new_node(mac):
            """Add Listener when a new Plugwise node joined the network."""
            device = device_registry.async_get_device({(DOMAIN, mac)}, set())
            hass.components.persistent_notification.async_create(
                title="New Plugwise device",
                message=(
                    "A new Plugwise device has been joined : \n\n"
                    f" - {api_stick.devices[mac].hardware_model} ({mac[-5:]})\n\n"
                    f"Configure this device at the [device dashboard](/config/devices/device/{device.id})"
                ),
            )

        api_stick.auto_update()

        if config_entry.pref_disable_new_entities:
            _LOGGER.debug("Configuring stick NOT to accept any new join requests")
            api_stick.allow_join_requests(True, False)
        else:
            _LOGGER.debug("Configuring stick to automatically accept new join requests")
            api_stick.allow_join_requests(True, True)
            api_stick.subscribe_stick_callback(add_new_node, CB_JOIN_REQUEST)

    def shutdown(event):
        hass.async_add_executor_job(api_stick.disconnect)

    api_stick = Stick(config_entry.data[CONF_USB_PATH])
    hass.data[DOMAIN][config_entry.entry_id] = {PW_TYPE: USB, STICK: api_stick}
    try:
        _LOGGER.debug("Connect to USB-Stick")
        await hass.async_add_executor_job(api_stick.connect)
        _LOGGER.debug("Initialize USB-stick")
        await hass.async_add_executor_job(api_stick.initialize_stick)
        _LOGGER.debug("Discover Circle+ node")
        await hass.async_add_executor_job(api_stick.initialize_circle_plus)
    except PortError:
        _LOGGER.error("Connecting to Plugwise USBstick communication failed")
        raise ConfigEntryNotReady from PortError
    except StickInitError:
        _LOGGER.error("Initializing of Plugwise USBstick communication failed")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady from StickInitError
    except NetworkDown:
        _LOGGER.warning("Plugwise zigbee network down")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady from NetworkDown
    except CirclePlusError:
        _LOGGER.warning("Failed to connect to Circle+ node")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady from CirclePlusError
    except TimeoutException:
        _LOGGER.warning("Timeout")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady from TimeoutException
    _LOGGER.debug("Start discovery of registered nodes")
    api_stick.scan(discover_finished)

    # Listen when EVENT_HOMEASSISTANT_STOP is fired
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, shutdown)

    # Listen for entry updates
    hass.data[DOMAIN][config_entry.entry_id][
        UNDO_UPDATE_LISTENER
    ] = config_entry.add_update_listener(_async_update_listener)

    async def device_add(service):
        """Manually add device to Plugwise zigbee network."""
        api_stick.node_join(service.data[ATTR_MAC_ADDRESS])

    async def device_remove(service):
        """Manually remove device from Plugwise zigbee network."""
        api_stick.node_unjoin(service.data[ATTR_MAC_ADDRESS])
        _LOGGER.debug(
            "Send request to remove device using mac %s from Plugwise network",
            service.data[ATTR_MAC_ADDRESS],
        )
        device_entry = device_registry.async_get_device(
            {(DOMAIN, service.data[ATTR_MAC_ADDRESS])}, set()
        )
        if device_entry:
            _LOGGER.debug(
                "Remove device %s from Home Assistant", service.data[ATTR_MAC_ADDRESS]
            )
            device_registry.async_remove_device(device_entry.id)

    hass.services.async_register(
        DOMAIN, SERVICE_USB_DEVICE_ADD, device_add, SERVICE_USB_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_USB_DEVICE_REMOVE, device_remove, SERVICE_USB_DEVICE_SCHEMA
    )

    return True


async def async_unload_entry_usb(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload the Plugwise stick connection."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS_USB
    )
    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()
    if unload_ok:
        api_stick = hass.data[DOMAIN][config_entry.entry_id]["stick"]
        await hass.async_add_executor_job(api_stick.disconnect)
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class PlugwiseUSBEntity(Entity):
    """Base class for Plugwise USB entities."""

    def __init__(
        self, node: PlugwiseNode, entity_description: PlugwiseEntityDescription
    ) -> None:
        """Initialize a Pluswise USB entity."""
        self._attr_available = node.available
        self._attr_device_info = {
            "identifiers": {(DOMAIN, node.mac)},
            "name": f"{node.hardware_model} ({node.mac})",
            "manufacturer": "Plugwise",
            "model": node.hardware_model,
            "sw_version": f"{node.firmware_version}",
        }
        self._attr_name = f"{entity_description.name} ({node.mac[-5:]})"
        self._attr_should_poll = entity_description.should_poll
        self._attr_unique_id = f"{node.mac}-{entity_description.key}"
        self._node = node
        self.entity_description = entity_description
        self.node_callbacks = (USB_ID.available, entity_description.key)

    async def async_added_to_hass(self):
        """Subscribe for updates."""
        for node_callback in self.node_callbacks:
            self._node.subscribe_callback(self.sensor_update, node_callback)

    async def async_will_remove_from_hass(self):
        """Unsubscribe to updates."""
        for node_callback in self.node_callbacks:
            self._node.unsubscribe_callback(self.sensor_update, node_callback)

    def sensor_update(self, state):
        """Handle status update of Entity."""
        self.schedule_update_ha_state()
        self._attr_available = self._node.available
