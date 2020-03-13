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
Traceback (most recent call last):
  File "/usr/src/homeassistant/homeassistant/helpers/update_coordinator.py", line 115, in async_refresh
    self.data = await self.update_method()
TypeError: async_safe_fetch() missing 1 required positional argument: 'api'

```

En dan van hieruit moeten we `PwThermostatSensor` weer proberen op te bouwen. Ik denk deels door de setup-code die er nog staat (maar niet meer gebruikt wordt) in de entry code te zetten, maar zo ver was ik dus nog niet
