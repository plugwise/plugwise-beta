
** Read the release notes (https://github.com/plugwise/plugwise-beta/releases) before upgrading, in case there are BREAKING changes! **

# Plugwise Smile custom_component (BETA)

Our main usage for this module is supporting [Home Assistant](https://www.home-assistant.io) / [home-assistant](http://github.com/home-assistant/core/)

 [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
 [![Generic badge](https://img.shields.io/github/v/release/plugwise/plugwise-beta)](https://github.com/plugwise/plugwise-beta)
 [![HASSfest](https://img.shields.io/badge/HASSfest%3F-view-blue.svg)](https://github.com/plugwise/plugwise-beta/actions)

A fully asynchronous approach to supporting Plugwise devices. This repository is **meant** for use of beta-testing. 

## NEW Oct 2020 ##
The developer of the Plugwise Stick integration, brefa, has joined the team. As a result we have added support for the Plugwise Stick.

## Sept 2020 ##
- Add a service: plugwise.delete_notification, this allows you to dismiss a Plugwise Notification from HA Core.
- Support for switching groups created on the Plugwise App has been added, these are available on the Adam with Plugs and on the Stretch.
- Support for the Plugwise Stretch v2 and v3 has been added.

## Aug 2020 ##
This custom_component can be installed to replace the HA Core Plugwise component. It can NO LONGER be installed next to the HA Core Plugwise component.
Due to this it behaves exactly as the HA Core Plugwise component: discovery works. But this beta-version has extra features and improvements!

PLEASE NOTE: ~~at the moment you will need to remove the existing Core Plugwise integration(s) before you install this beta custom_component. This is at the moment also needed when you want to return to using the Core Plugwise integration. When this is no longer needed, you can read about it here.~~ Since Core v0.115.0 this is no longer needed.

### Required python module (status)

 [![Build Status](https://travis-ci.org/plugwise/Plugwise-Smile.svg?branch=master)](https://travis-ci.org/plugwise/Plugwise-Smile)
 [![codecov](https://codecov.io/gh/plugwise/Plugwise-Smile/branch/master/graph/badge.svg)](https://codecov.io/gh/plugwise/Plugwise-Smile)
 [![PyPI version fury.io](https://badge.fury.io/py/Plugwise-Smile.svg)](https://pypi.python.org/pypi/Plugwise-Smile/)

## What do we support (in short)?

  - Adam (firmware 2.3 + 3.0) and the accompanying Lisa's, Tom's, Floor's, Koen's and Plugs.
  - Smile & Anna (firmware 1.8, 3.1 and 4.0)
    - Plugwise Notifications from the Adam and the Anna
  - Smile P1 (firmware 2.1, 2.5, 3.3 and 4.0)
  - Stretch (firmware 2.3 and 3.1)
  - Stick

## What can I expect in HA Core from this component

  - `climate`: A (number of) thermostat(s) visible in HA, including temperature, presets and heating-demand status, per thermostat. Also, setting of temperature, preset and switching the active schedule on and off. Cooling is only supported in combination with an Anna (fw 3.1 and 4.0).
  - `sensor` and `binary_sensor`: A number of sensoric values depending on your hardware: outdoor temperature, Anna's illuminance, Tom's valve postion, Plug's and Circle/Stealth's power-values, P1 power- and gas-values, Plugwise Notifications.
  - `switch`: The switch-parts of Plugs/Circles are available as switches, also switching them on/off is supported.

The `water_heater`-device present in previous releases has been replaced by an Auxiliary Device state-sensor. This sensor will only show up when there are more (than one) thermostats present in your climate-system.

## How to install?

 - Use [HACS](https://hacs.xyz) 
 - Use the link to this page and add it on the `custom repo` page .
 - Look for `Plugwise beta custom component ` in `integrations` and install it!

## How to add the integration to HA Core

For each Plugwise Smile (i.e. gateway) you will have to add it as an integration. For instance if you have an Adam and a Smile P1, you have to add them individually. If you have an Anna and an Adam, do not add the Anna, only add the Adam.
 - [ ] In Home Assitant click on `Configuration`
 - [ ] Click on `Integrations`
 - [ ] You should see one or more discovered Smiles
 - [ ] Click the `Configure` button and enter the Smile ID
 - [ ] Click Add to see the magic happens
 
 If there is no discovered Smile present:
 - [ ] Hit the `+` button in the right lower corner
 - [ ] Search or browse for 'Plugwise beta' and click it
 - [ ] Select the type of integration: Network or USB
 - For the Network-selection:
 - [ ] Enter your Smile IP-address and the 8 character ID of the smile
 - [ ] Click SUBMIT and FINISH and hopefully the magic happens
 - [ ] Repeat this process to add more Smiles
 - For the USB-selection:
 - [ ] Select or enter the USB-path
 - [ ] Click SUBMIT and FINISH

HA Core wil continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

## Options ##

Using the OPTIONS-button, the default Smile-data refresh-interval can be modified. There are no OPTIONS available for the Stick.

# I don't like the name of the sensor or the icon

You can adjust these in `Configuration`, `Integration` -> `Entities` (e.g. `https://{Your HA address}/config/entities`)

Just click on the device and adjust accordingly!

# It doesn't work

If you notice issuess, we are on discord and on the Community. You can also create an Issue in these repos:

  - [plugwise-beta](https://github.com/plugwise/plugwise-beta) - the `custom_component` for HA Core
  - [Plugwise-Smile](https://github.com/plugwise/Plugwise-Smile) - the python module interfacing between the plugwise component and your Smile

# Smile?

We use the term Smile for the 'device connected to your home network', called Smile P1 for their power-meter, Smile if you have an Anna or Adam.

# Testing

While we try to make sure that everyting works as intended, we can't really test out changes happening to hardware devices. Our testing is done through testing against files from community members (see [Plugwise-Smile tests](https://github.com/plugwise/Plugwise-Smile/tree/master/tests)) and if you have a setup you are willing to share we highly welcome that. Just send us the files or submit a PR. Including your testcode into the `tests/test_Smile.py` code is highly recommended.

Results of our tests are checked by Travis, click the left button (the one that should say 'Build passing' :)) on the [Plugwise-Smile repository](https://github.com/plugwise/Plugwise-Smile/).

# ~~There is Anna support in HA Core already~~ Replaced by the new Plugwise component, based on this beta-version.

And from the original sources by @laetificat it was improved upon and upstreamed by @CoMPaTech and improved and maintained by @bouwew

As things like async were in high demand from HA Core, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Smile Beta repository (accompanying the Plugwise-Smile python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module).

And yes anna-ha with haanna (to some degree) support Anna v1.8 - but they don't support Adam nor the Smile P1
