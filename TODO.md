# Todo's configentry ombouw

Config entry gaat nu ook met frontend. Dus je moet naar `Settings` -> `Integrations` -> `Plugwise HA`

De velden zijn nu: (geen idee waarom de placeholders niet getoond worden, referentie `components/icloud/strings.json`)

 - Naam: (default is Smile maar je kunt hier Adam tikken)
 - IP-adres: 192.168.x.y
 - Secret: de 8 lettercode
 - Timeout: nu nog default op 30
 - Keuzeveldje: wijst vanzelf

**Aangepast zijn nu**

`__init.py__` volgens nieuwe opzet, `config_flow.py` is erbij gekomen (samen met `strings.json` en een extra regel in `manifest.json`

Volgorde is `config_flow` die roept de setup entry in `__init__` aan en die doet wat hij al deed met nu alleen `sensor` aanroepen (ff klein beginnen)

 - [ ] Todo: In `config_flow.py` in de validatie zorgen dat je alleen thermostaat of power kunt kiezen
 - [ ] Todo: In `config_flow.py` later nog een keer zorgen dat legacy er bij komt

 - [ ] FIXME: In `sensor.py` ben ik ergens met scaffolding gestopt, onderstaande foutmelding was er nu nog maar het was stoptijd voor vanavond

Foutmelding:

```
enumerate van data gaat niet goed

2020-03-14 10:18:06 DEBUG (MainThread) [custom_components.Plugwise-HA.sensor] Finished fetching sensor data in 0.169 seconds
2020-03-14 10:18:06 DEBUG (MainThread) [custom_components.Plugwise-HA.sensor] Sensorcoordinator <homeassistant.helpers.update_coordinator.DataUpdateCoordinator object at 0x7fe4b6cb7d50>
2020-03-14 10:18:06 DEBUG (MainThread) [custom_components.Plugwise-HA.sensor] Sensorcoordinator data True
2020-03-14 10:18:06 ERROR (MainThread) [homeassistant.components.sensor] Error while setting up Plugwise-HA platform for sensor
Traceback (most recent call last):
  File "/usr/src/homeassistant/homeassistant/helpers/entity_platform.py", line 179, in _async_setup_platform
    await asyncio.wait_for(asyncio.shield(task), SLOW_SETUP_MAX_WAIT)
  File "/usr/local/lib/python3.7/asyncio/tasks.py", line 442, in wait_for
    return fut.result()
  File "/config/custom_components/Plugwise-HA/sensor.py", line 104, in async_setup_entry
    _LOGGER.debug('Sensorcoordinator data enum %s',enumerate(sensor_coordinator.data))
TypeError: 'bool' object is not iterable

diffen https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities vs hue/light.py

```

En dan van hieruit moeten we `PwThermostatSensor` weer proberen op te bouwen. Ik denk deels door de setup-code die er nog staat (maar niet meer gebruikt wordt) in de entry code te zetten, maar zo ver was ik dus nog niet
