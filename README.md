**New** Configure using integrations!

# Plugwise Smile Beta

A fully asynchronous approach to supporting Plugwise devices. At this time we only support the newest firmware (_unfortunat_ but as the developers only have recent hardware it takes time to develop for 'legacy' devices).

What do we support?

  - Adam (firmware 2.3 + 3.0)
  - Smile & Anna (firmware 3.1)
  - Smile P1 (firmware 3.3)

What is on our radar (not commitment to timelines though)

  - Smile & Anna (v1.8)
  - Smile P1 (v2.5)

What can I expect in HA

  - `climate`: A (number of) thermostat(s) visible in HA, including temperature, presets and heating status
  - `sensor`:A number of sensoric values depending on your hardware (Outdoor temperature, Anna's illuminance, plug power-usage, P1 values)
  - `switch`: Plugs available as switches (functionality determined as configured through the Mobile Plugwise App and/or web-interface)
  - `water_heater`: 

## How to set-up?

 - Use [HACS](https://hacs.xyz) to install this repo and make this `custom_component` available!

## When installed

 - [ ] In Home Assitant click on `Configuration`
 - [ ] Click on `Integrations`
 - [ ] Hit the `+` button in the corner
 - [ ] Search or browse for 'Plugwise Smile beta' and click it
 - [ ] Enter your Smiles IP-address and the 8 character ID of the smile
 - [ ] Click Add and hopefully the magic happens

HA wil continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

# It doesn't work

It's still in early phases and moving between two developers and a handfull of testers, if you notice things we are on discord and welcome issues on the repos

  - [plugwise-beta](https://github.com/plugwise/plugwise-beta) - the `custom_component` for Home Assistant
  - [Plugwise-Smile](https://github.com/plugwise/Plugwise-Smile) - the python module interfacing between the component and your Smile

# Smile?

We use the term Smile for the 'device connected to your home network', called Smile P1 for their power-meter, Smile if you have an Anna or Adam.

# There is Anna support in HA Core already

And from the original sources by @laetificat it was upstreamed by @CoMPaTech and maintained by @bouwew

As things like async were in high demand from HA, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Smile Beta repository (accompanying the Plugwise-Smile python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module).

And yes this (to some degree) supports Anna v1.8 - it doesn't support Adam nor the Smile P1
