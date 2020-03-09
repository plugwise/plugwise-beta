"""Plugwise components for Home Assistant Core."""

import logging
import asyncio

import voluptuous as vol
from Plugwise_Smile.Smile import Smile

from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
)

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_USERNAME,
    DEFAULT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_THERMOSTAT,

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

    if CONF_THERMOSTAT in conf:
        thermostats = conf[CONF_THERMOSTAT]

        _LOGGER.info('Plugwise Thermostats %s',thermostats)
        hass.data[DOMAIN][CONF_THERMOSTAT] = {}

        for thermostat in thermostats:
            _LOGGER.info('Plugwise Thermostat %s',thermostat)
            smile_config=thermostat[0]

        
            websession = async_get_clientsession(hass, verify_ssl=False)
            plugwise_data_connection = Smile(host=smile_config[CONF_HOST],password=smile_config[CONF_PASSWORD],websession=websession)

            _LOGGER.debug("Plugwise connecting %s",smile_config)
            if not await plugwise_data_connection.connect():
                _LOGGER.error("Failed to connect to Plugwise")
                return

            hass.data[DOMAIN]['thermostat'][smile_config[CONF_NAME]] = { 'data_connection': plugwise_data_connection }

            for component in PLUGWISE_COMPONENTS:
                hass.helpers.discovery.load_platform(
                    component, DOMAIN, {}, config,
                )

            _LOGGER.info('Plugwise Smile config: %s',config)
            _LOGGER.info('Plugwise Smile smile config: %s',smile_config)
    #  We should handle P1 sometime
    else:
       return False

    return True


