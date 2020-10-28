"""Support for Plugwise devices connected to a Plugwise USB-stick."""
import asyncio
import logging
import voluptuous as vol

import plugwise
from plugwise.exceptions import (
    CirclePlusError,
    NetworkDown,
    PortError,
    StickInitError,
    TimeoutException,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_STATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_DEVICE_CLASS,
    ATTR_ENABLED_DEFAULT,
    ATTR_ICON,
    ATTR_MAC_ADDRESS,
    ATTR_NAME,
    CONF_USB_PATH,
    DOMAIN,
    PLATFORMS_USB,
    PW_TYPE,
    SERVICE_DEVICE_ADD,
    SERVICE_DEVICE_REMOVE,
    UNDO_UPDATE_LISTENER,
    STICK,
    STICK_API,
    USB,
    USB_AVAILABLE_ID,
    USB_MOTION_ID,
    USB_RELAY_ID,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry_usb(hass: HomeAssistant, config_entry: ConfigEntry):
    """Establish connection with plugwise USB-stick."""
    hass.data.setdefault(DOMAIN, {})
    device_registry = await dr.async_get_registry(hass)

    def discover_finished():
        """Create entities for all discovered nodes."""
        _LOGGER.debug(
            "Successfully discovered %s out of %s registered nodes",
            str(len(api_stick.discovered_nodes)),
            str(api_stick.joined_nodes),
        )
        for component in PLATFORMS_USB:
            hass.data[DOMAIN][config_entry.entry_id][component] = []

        for mac in api_stick.discovered_nodes:
            if USB_RELAY_ID in api_stick.node(mac).features:
                hass.data[DOMAIN][config_entry.entry_id]["switch"].append(mac)
            if USB_MOTION_ID in api_stick.node(mac).features:
                hass.data[DOMAIN][config_entry.entry_id]["binary_sensor"].append(mac)
            hass.data[DOMAIN][config_entry.entry_id]["sensor"].append(mac)

        for component in PLATFORMS_USB:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, component)
            )
        api_stick.auto_update()

        if config_entry.system_options.disable_new_entities:
            _LOGGER.debug("Configuring stick NOT to accept any new join requests")
            api_stick.allow_join_requests(True, False)
        else:
            _LOGGER.debug("Configuring stick to automatically accept new join requests")
            api_stick.allow_join_requests(True, True)

    def shutdown(event):
        hass.async_add_executor_job(api_stick.disconnect)

    api_stick = plugwise.stick(config_entry.data[CONF_USB_PATH])
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
        raise ConfigEntryNotReady
    except StickInitError:
        _LOGGER.error("Initializing of Plugwise USBstick communication failed")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady
    except NetworkDown:
        _LOGGER.warning("Plugwise zigbee network down")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady
    except CirclePlusError:
        _LOGGER.warning("Failed to connect to Circle+ node")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady
    except TimeoutException:
        _LOGGER.warning("Timeout")
        await hass.async_add_executor_job(api_stick.disconnect)
        raise ConfigEntryNotReady
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
        device_entry = device_registry.async_get_device(
            {(DOMAIN, service.data[ATTR_MAC_ADDRESS])}, set()
        )
        if device_entry:
            _LOGGER.debug("Remove device %s from Home Assistant", service.data[ATTR_MAC_ADDRESS])
            device_registry.async_remove_device(device_entry.id)

    service_device_schema = vol.Schema({vol.Required(ATTR_MAC_ADDRESS): cv.string})

    if config_entry.system_options.disable_new_entities:
        hass.services.async_register(
            DOMAIN, SERVICE_DEVICE_ADD, device_add, service_device_schema
        )
    hass.services.async_register(
        DOMAIN, SERVICE_DEVICE_REMOVE, device_remove, service_device_schema
    )

    return True


async def async_unload_entry_usb(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload the Plugwise stick connection."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS_USB
            ]
        )
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


class NodeEntity(Entity):
    """Base class for a Plugwise entities."""

    def __init__(self, node, api_type):
        """Initialize a Node entity."""
        self._node = node
        self._api_type = api_type
        self.node_callbacks = None

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        for node_callback in self.node_callbacks:
            self._node.subscribe_callback(self.sensor_update, node_callback)

    async def async_will_remove_from_hass(self):
        """Unsubscribe to updates."""
        for node_callback in self.node_callbacks:
            self._node.unsubscribe_callback(self.sensor_update, node_callback)

    @property
    def available(self):
        """Return the availability of this entity."""
        return getattr(self._node, STICK_API[USB_AVAILABLE_ID][ATTR_STATE])

    @property
    def device_class(self):
        """Return the device class of the binary sensor."""
        return STICK_API[self._api_type][ATTR_DEVICE_CLASS]

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._node.mac)},
            "name": f"{self._node.hardware_model} ({self._node.mac})",
            "manufacturer": "Plugwise",
            "model": self._node.hardware_model,
            "sw_version": f"{self._node.firmware_version}",
        }

    @property
    def entity_registry_enabled_default(self):
        """Return the binary sensor registration state."""
        return STICK_API[self._api_type][ATTR_ENABLED_DEFAULT]

    @property
    def icon(self):
        """Return the icon."""
        return (
            None
            if STICK_API[self._api_type][ATTR_DEVICE_CLASS]
            else STICK_API[self._api_type][ATTR_ICON]
        )

    @property
    def name(self):
        """Return the display name of this entity."""
        return f"{STICK_API[self._api_type][ATTR_NAME]} ({self._node.mac[-5:]})"

    def sensor_update(self, state):
        """Handle status update of Entity."""
        self.schedule_update_ha_state()

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def unique_id(self):
        """Get unique ID."""
        return f"{self._node.mac}-{self._node.hardware_model}"
