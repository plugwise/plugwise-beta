
** Read the 0.2.x release notes (https://github.com/plugwise/plugwise-beta/releases/tag/0.2.0) before upgrading - you should always read them, but 0.2.x is a breaking upgrade (and requires HA 0.109)! **

# Plugwise Smile custom_component (BETA)

Our main usage for this module is supporting [Home Assistant](https://www.home-assistant.io) / [home-assistant](http://github.com/home-assistant/core/)

 [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
 [![Generic badge](https://img.shields.io/github/v/release/plugwise/plugwise-beta)](https://github.com/plugwise/plugwise-beta)
 [![HASSfest](https://img.shields.io/badge/HASSfest%3F-view-blue.svg)](https://github.com/plugwise/plugwise-beta/actions)

A fully asynchronous approach to supporting Plugwise devices. This repository is **meant** for use of beta-testing. 

## Status

 - [x] The current (feb/mar/apr 2020) `plugwise` HA-core component only supports Anna devices (both v1 and v3)
 - [x] This module supports all devices as indicated on the [Plugwise-Smile](https://github.com/plugwise/Plugwise-Smile) repository page
 - [ ] [PR](https://github.com/home-assistant/core/pull/33691) for HA-core is out, but we will continue ironing out the kinks together with **you** using this `custom_module`

### Required python module (status)

 [![Build Status](https://travis-ci.org/plugwise/Plugwise-Smile.svg?branch=master)](https://travis-ci.org/plugwise/Plugwise-Smile)
 [![codecov](https://codecov.io/gh/plugwise/Plugwise-Smile/branch/master/graph/badge.svg)](https://codecov.io/gh/plugwise/Plugwise-Smile)
 [![PyPI version fury.io](https://badge.fury.io/py/Plugwise-Smile.svg)](https://pypi.python.org/pypi/Plugwise-Smile/)

## What do we support (in short)?

  - Adam (firmware 2.3 + 3.0)
  - Smile & Anna (firmware 1.8, 3.1 and 4.0)
  - Smile P1 (firmware 2.5 and 3.3)

## What can I expect in HA from this component

  - `climate`: A (number of) thermostat(s) visible in HA, including temperature, presets and heating-demand status, per thermostat. Also, setting of temperature, preset and switching the active schedule on and off. Cooling is only supported in combination with an Anna (fw 3.1 and 4.0).
  - `sensor` and `binary_sensor`: A number of sensoric values depending on your hardware: outdoor temperature, Anna's illuminance, Tom's valve postion, Plug's power-values, P1 power- and gas-values
  - `switch`: The switch-parts of Plugs are available as switches, also switching them on/off is supported.

The `water_heater`-device present in previous releases has been replaced by a state-sensor. This sensor will only show up when there are more (than one) thermostats present in your climate-system.

## How to set-up?

 - Use [HACS](https://hacs.xyz) 
 - Use the link to this page and add it on the `custom repo` page .
 - Look for `Plugwise beta custom component ` in `integrations` and install it!
 - If you need an pre-release for testing, click the three dots and mark the 'beta' check to see pre-releases.

## When installed

For each Plugwise Smile (i.e. gateway) you have add an integration. For instance if you have an Adam and a Smile P1, you have to add them individually.

 - [ ] In Home Assitant click on `Configuration`
 - [ ] Click on `Integrations`
 - [ ] Hit the `+` button in the corner
 - [ ] Search or browse for 'Plugwise Smile beta' and click it
 - [ ] Enter your Smiles IP-address and the 8 character ID of the smile
 - [ ] Click Add and hopefully the magic happens

HA wil continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

# I don't like the name of the sensor or the icon

You can adjust these in `Configuration`, `Integration` -> `Entities` (e.g. `https://{Your HA address}/config/entities`)

Just click on the device and adjust accordingly!

# It doesn't work

It's still in early phases and moving between two developers and a handfull of testers, if you notice things we are on discord and welcome issues on the repos

  - [plugwise-beta](https://github.com/plugwise/plugwise-beta) - the `custom_component` for Home Assistant
  - [Plugwise-Smile](https://github.com/plugwise/Plugwise-Smile) - the python module interfacing between the component and your Smile

# Smile?

We use the term Smile for the 'device connected to your home network', called Smile P1 for their power-meter, Smile if you have an Anna or Adam.

# Testing

While we try to make sure that everyting works as intended, we can't really test out changes happening to hardware devices. Our testing is done through testing against files from community members (see [Plugwise-Smile tests](https://github.com/plugwise/Plugwise-Smile/tree/master/tests)) and if you have a setup you are willing to share we highly welcome that. Just send us the files or submit a PR. Including your testcode into the `tests/test_Smile.py` code is highly recommended.

Results of our tests are checked by Travis, click the left button (the one that should say 'Build passing' :)) on the [Plugwise-Smile repository](https://github.com/plugwise/Plugwise-Smile/).

# There is Anna support in HA Core already

And from the original sources by @laetificat it was improved upon and upstreamed by @CoMPaTech and improved and maintained by @bouwew

As things like async were in high demand from HA, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Smile Beta repository (accompanying the Plugwise-Smile python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module).

And yes anna-ha with haanna (to some degree) support Anna v1.8 - but they don't support Adam nor the Smile P1
