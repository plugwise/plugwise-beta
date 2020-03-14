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

 - [ ] Sensors van thermostat werken, maar nog zorgen dat de sensor.py code meekrijgt of het thermostat of power is (en/of dat in Smile.py fietsen)
 - [ ] Sensors testen met power (maar daarvoor eerst bovenstaande oplossen)

