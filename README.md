# Configuration file `configuration.yaml` entry

```
Plugwise-HA:
  thermostat:
    - name: My Anna
      password: abcdefgh
      host: 192.168.1.2
    - name: Their Adam
      password: abcdefgh
      host: 192.168.1.2
```

Optional:

```
Plugwise-HA:
  thermostat:
    - name: My Anna
      password: abcdefgh
      host: 192.168.1.2
      scan_interval: 30      # Defaults to 60
      username: someone      # Defaults to smile
      port: 81               # Defaults to 80
      heater: False          # Defaults to True - if you don't have a boiler set to False to skip the water_heater component
  power:
    - name: My P1
      password: abcdefgh
      host: 192.168.1.2
      solar: False           # Defaults to True - if you don't have solar panels set to False to skip sensors
      gas: False             # Defaults to True - if you don't have gas at home, set to False to skip sensors
```
