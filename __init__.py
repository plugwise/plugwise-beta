"""Plugwise components for Home Assistant Core."""

import logging
import asyncio
import async_timeout

from datetime import timedelta

import voluptuous as vol
from Plugwise_Smile.Smile import Smile


from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from homeassistant.helpers import config_validation as cv

from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
)

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_USERNAME,
    DEFAULT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_SCAN_INTERVAL,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_THERMOSTAT,
    CONF_POWER,
    CONF_HEATER,

)

from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

# HVAC modes
HVAC_MODES_1 = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
HVAC_MODES_2 = [HVAC_MODE_HEAT_COOL, HVAC_MODE_AUTO]

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE)

PLUGWISE_CONFIG = vol.Schema(
        {
            vol.Optional(
                CONF_NAME, default=DEFAULT_NAME
            ): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(
                CONF_PORT, default=DEFAULT_PORT
            ): cv.port,
            vol.Optional(
                CONF_USERNAME, default=DEFAULT_USERNAME
            ): cv.string,
            vol.Optional(CONF_HEATER, default=True): cv.boolean,
            vol.Optional(
                CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
            ): cv.time_period,
        }
)

# Read platform configuration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
        {
                vol.Optional(CONF_THERMOSTAT): vol.All(
                    cv.ensure_list,
                    [
                        vol.All(
                            cv.ensure_list, [PLUGWISE_CONFIG],
                        ),
                    ],
                ),
                vol.Optional(CONF_POWER): vol.All(
                    cv.ensure_list,
                    [
                        vol.All(
                            cv.ensure_list, [PLUGWISE_CONFIG],
                        ),
                    ],
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLUGWISE_COMPONENTS = ["climate", "water_heater", "sensor"]

@asyncio.coroutine
async def async_setup(hass, config):
    """Add the Plugwise Gateways."""

    conf = config.get(DOMAIN)

    if conf is None:
        raise PlatformNotReady

    _LOGGER.info('Plugwise %s',conf)
    hass.data[DOMAIN] = {}

    for smile_type,smile_config in conf.items():
        _LOGGER.info('Plugwise Smile type %s',smile_type)
        _LOGGER.info('Plugwise Smile setup %s',smile_config)
        hass.data[DOMAIN][smile_type] = {}
        for smile in smile_config:
            _LOGGER.info('Plugwise smile %s',smile)
            smile=smile[0]
            smile['type']=smile_type

            websession = async_get_clientsession(hass, verify_ssl=False)
            plugwise_data_connection = Smile(host=smile[CONF_HOST],password=smile[CONF_PASSWORD],websession=websession)

            _LOGGER.debug("Plugwise connecting to %s",smile)
            if not await plugwise_data_connection.connect():
                _LOGGER.error("Failed to connect to %s Plugwise Smile",smile_type)
                return

            hass.data[DOMAIN][smile_type][smile[CONF_NAME]] = { 'data_connection': plugwise_data_connection, 'type': smile_type, 'water_heater': smile[CONF_HEATER] }

            _LOGGER.info('Plugwise Smile smile config: %s',smile)

            async def async_update_data():
                """Fetch data from Smile"""
                async with async_timeout.timeout(10):
                    return await plugwise_data_connection.full_update_device()

            _LOGGER.info('Plugwise scan interval: %s',smile[CONF_SCAN_INTERVAL])
            coordinator = DataUpdateCoordinator(
                hass,
                _LOGGER,
                name='{}_{}'.format(DOMAIN,smile[CONF_NAME]),
                update_method=async_update_data,
                update_interval=smile[CONF_SCAN_INTERVAL],
            )

            # Fetch initial data so we have data when entities subscribe
            await coordinator.async_refresh()

    for component in PLUGWISE_COMPONENTS:
        hass.helpers.discovery.load_platform(
            component, DOMAIN, {}, config,
        )


    return True

