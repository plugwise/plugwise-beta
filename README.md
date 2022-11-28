
**:warning::warning::warning:Read the [release notes](<https://github.com/plugwise/plugwise-beta/releases>) before upgrading, in case there are BREAKING changes!:warning::warning::warning:**

# Plugwise custom_component (BETA)

A fully asynchronous approach to supporting Plugwise devices in Home-Assistant. This repository is **meant** for use of beta-testing. As of March 2021 we include testing against latest `dev` in Home-Assistant Core, the above batches should indicate compatibility and compliance.

 [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
 [![CodeFactor](https://www.codefactor.io/repository/github/plugwise/plugwise-beta/badge)](https://www.codefactor.io/repository/github/plugwise/plugwise-beta)
 [![HASSfest](https://github.com/plugwise/plugwise-beta/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/plugwise/plugwise-beta/actions)
 [![HA-Core](https://github.com/plugwise/plugwise-beta/workflows/Test%20with%20HA-core/badge.svg)](https://github.com/plugwise/plugwise-beta/actions)
 [![Generic badge](https://img.shields.io/github/v/release/plugwise/plugwise-beta)](https://github.com/plugwise/plugwise-beta)

Always first attempt to use the native [Home Assistant](https://www.home-assistant.io/integrations/plugwise/)-component using this button 

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/) 

If you don't mind a bug now and then and are interested in helping us test new features and improvements, you can start using this BETA `custom_component`. We develop and maintain both versions.

## Required python module (status)

Our [`python-plugwise`](https://github.com/plugwise/python-plugwise) python module accompanies both the native and the `custom_component`. It's status is is:

 [![Latest release](https://github.com/plugwise/python-plugwise/workflows/Latest%20release/badge.svg)](https://github.com/plugwise/python-plugwise/actions)
 [![CodeFactor](https://www.codefactor.io/repository/github/plugwise/python-plugwise/badge)](https://www.codefactor.io/repository/github/plugwise/python-plugwise)
 [![codecov](https://codecov.io/gh/plugwise/python-plugwise/branch/main/graph/badge.svg)](https://codecov.io/gh/plugwise/python-plugwise)
 [![PyPI version fury.io](https://badge.fury.io/py/plugwise.svg)](https://pypi.python.org/pypi/plugwise/)

# Changelog

# NEW NOV 2022 [0.31.4] Bugfixes, improve exception-handling
- Bugfixes via plugwise v0.25.12 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.10

# NOV 2022 [0.31.3] Thermostats: more improvements
- Anna+Elga: remove cooling-switch, add cooling_enabled binary_sensor (NOTE: reload integration every time the cooling-enabled switch position on the Elga is changed)
- Link to plugwise v0.25.10 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.10
  - Fixes for https://github.com/plugwise/python-plugwise/issues/240, https://github.com/home-assistant/core/issues/81716, https://github.com/home-assistant/core/issues/81839, https://github.com/home-assistant/core/issues/81672, https://github.com/plugwise/python-plugwise/issues/241

# NOV 2022 not released [0.31.2] Bug-fixes
- Adam: hide cooling-related switch, binary_sensors when there is no cooling present, this fixes the unexpected appearance of new entities after the Adam 3.7.1 firmware-update.
- Properly handle an empty schedule, should fix #313
- Link to plugwise v0.25.9 - not released
- Link to plugwise v0.25.8 - not released

# NOV 2022 [0.31.1] Bugfix for Core issue #81531
- Fix wrong logic in v0.25.7 - via https://github.com/plugwise/python-plugwise/releases/tag/v0.25.7
- Fix bug via plugwise v0.25.6 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.6
- Implement Core PR #80722

# OCT 2022 [0.31.0] Change to hvac_mode heat_cool, improvements and bugfixes
- Implement hvac_mode heat_cool for heating + cooling as required by HA Core
- Fix for plugwise/plugwise-beta#309 via plugwise v0.25.3 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.3
- Fix heat_cool-related bug via plugwise v0.25.2 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.2
- Link to plugwise v0.25.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.1
- Link to plugwise v0.25.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.25.0
- Fix for home-assistant/core#79708 via plugwise v0.24.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.24.1
- Follow lastest HA Core Plugwise changes

# OCT 2022 [0.30.1] Bugfix in plugwise v0.24.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.24.1

# OCT 2022 [0.30.0] Improve support for Anna-Loria combination
- Enable Plugiwse notifications for non-legacy Smile P1's
- Link to plugwise v0.24.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.24.0

# OCT 2022 [0.29.0] Non-legacy Smiles: introduce device availability
- Adam: Re-add vacation-preset (following change in the Plugwise App)
- Link to plugwise v0.23.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.23.0

# Sept 2022 [0.28.0]
- Smile P1: change to two devices, rename/streamline device names and models - via plugwise v0.22.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.22.1

# Sept 2022 [0.27.0] 
- Implement https://github.com/home-assistant/core/pull/75109 via plugwise v0.21.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.21.1
- Implement https://github.com/home-assistant/core/pull/75161
- Climate:  implementing the new Climate classes `ClimateEntityFeature`,  `HVACAction`, and `HVACMode`.
- Climate: fix bug in `hvac_modes` determination, implement changes from plugwise v0.21.1
- Climate: `async_set_temperature()`: support `hvac_mode`-change
- Refresh test fixtures
- Adapt tests/asserts
- Adapt to recent DUC changes wrt error handling
- DUC: provide a single error-message (platinum requirement) when the connection is lost (a single return-message is not needed, provided by the DUC)
- Fix cooldown-interval is None at init, raise max. to 10 (max in Core)
- Follow https://github.com/home-assistant/core/pull/76610 (link to plugwise v0.21.3, simplify/revert cooling-related code)
- Implement https://github.com/home-assistant/core/pull/78680
- Implement https://github.com/home-assistant/core/pull/78935

# July 2022 [0.26.0]
- Smile: Add domestic_hot_water_setpoint Number, further fix cooling support.
  - Link to plugwise v0.21.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.21.0
  - Add domestic_hot_water_setpoint Number, update/simplify number-set-value function.
  - Fix cooling support for Anna + Elga (user-tested).

# July 2022 [0.25.2b0]
- Smile: NumberEntity, config_flow test updates
  - Implement NumberEntity updates from Core
  - Implement FlowResultType in config_flow test (Core PR #74638)
  - HACS: bump minimum Core version to 2022.7.0

# July 2022 [0.25.1b0]
- Smile: fix/improve cooling support - via plugwise v0.20.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.20.1

# June 2022 [0.25.0]
- Adam: add support for the Aqara Plug - via plugwise v0.20.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.20.0

# June 2022 [0.24.2]
- Stick: fix async_get_registry warning in Core Log

# June 2022 [0.24.1]
- Smiles & Stretches: clean up & improve error handling/reporting
  - Link to plugwise v0.19.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.19.1

# June 2022 [0.24.0]
- Smile Anna cooling-related updates
  - Link to plugwise v0.19.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.19.0
  - For the Anna with Elga combination, add a CONFIGURE option `cooling on`. Select this option to let the Plugwise integration know that the cooling-feature of your Elga has been set to on. 
  - Show `target_temp_high` and `target_temp_low` instead of `target_temperature`, when cooling is active, next to heating.
  - Add the `supported_features` as a property as they can change when the cooling-feature (on the Elga/Loria/Thermastage) is turned on or off.

# MAY 2022 [0.23.2]
- Smile bugfix: fixing https://github.com/plugwise/python-plugwise/issues/192 and https://github.com/home-assistant/core/issues/72305
  via plugwise v0.18.5 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.5

# MAY 2022 [0.23.1]
- Smile: improve testcoverage, correct a small bug in climate.py

# MAY 2022 [0.23.0]
- Smile: rework & improve plugwise backend - via plugwise v0.18.0 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.0
  - Adam: don't show vacation-preset - via plugwise v0.18.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.1
  - Fix handling of a connection-issue - via plugwise v0.18.2 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.2
- Implement Core PR https://github.com/home-assistant/core/pull/70975
- Set coordinator cooldown time to 5.0 secs, this should allow for showing the correct climate status on the Core frontend after a manual change (in temperature setpoint, preset, schedule) after 5 seconds.
- Update number.py and select.py (add tests) based on review-feedback on changes in https://github.com/home-assistant/core/pull/69210
- Fix issues https://github.com/plugwise/plugwise-beta/issues/276 and https://github.com/plugwise/plugwise-beta/issues/280 - via plugwise v0.18.3 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.3
- Speed up data collection - via plugwise v0.18.4 - https://github.com/plugwise/python-plugwise/releases/tag/v0.18.4
- Climate: move error-handling of set-functions to backend - via plugwise v0.18.4
- Smile Anna & Adam: provide the Frontend refresh-interval as a settable parameter via the CONFIGURE button (1.5 to 5 seconds).
- Add tests for the select-platform.

## APR 2022 [0.22.4]
- Smile: Stretch bugfix, solving #277 via plugwise v0.17.8 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.8

## APR 2022 [0.22.3]
- Smile:
  - Link to plugwise v0.17.7 and adapt to changes (fixtures, tests) - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.7
  - Add (back) compressor_state as binary_sensor (Anna - heat-pump)
  - Implement HA Core PR #70366 fixing connectivity issues (should also fix issues #268, #274)
  - Improvements in climate-code

## APR 2022 [0.22.2]
- Smile:
  - Climate: filter/report invalid options when using the HA climate service functions
  - Climate: improve generation of the hvac_modes list:
    - Improve support for the cooling implementations of the Adam (manual) and the Anna (automatic)
    - Make hvac_modes a property as the contents of the hvac_modes list isn't fixed
  - Integration: fix CONFIGURE options not working

## APR 2022 [0.22.1]
- Smile:
  - Link to plugwise v0.17.6 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.6
  - Link to plugwise v0.17.5 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.5
  - Link to plugwise v0.17.3 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.3
  - Implement https://github.com/home-assistant/core/pull/69094
  - Code improvements based on HA Core 2022.4.0

## MAR 2022 [0.22.0]
- Smile:
  - Link to plugwise v0.17.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.1, fixing https://github.com/home-assistant/core/issues/68621
  - Link to plugwise v0.17.2 - https://github.com/plugwise/python-plugwise/releases/tag/v0.17.2
  - Rework select.py, add selector for the heating/cooling-system regulation mode.
  - Add number.py (and tests), provide an option for changing the maximum boiler (water) temperature setpoint.
  - Remove climate schedule attributes, moved to the options-attribute of the select schedule entity.
  - Implement fix for the sticking HA persistent notifications
  - Only show HVAC_MODE off for HomeKit emulation

## MAR 2022 [0.21.5]
 - Smile:
  - **BREAKING** improved naming of the locally present outdoor temp sensor connected to the OpenTherm device: `outdoor_air_temperature`. The former `sensor.opentherm_outdoor_temperature` is now visible as `sensor.opentherm_outdoor_air_temperature`. Use of the zipcode based `outdoor_temperature` has not changed.
  - **POTENTIALLY BREAKING** for consistency renamed schema to schedule, i.e. the attributes will now be `available_schedules` and `selected_schedule`.
  - Link to plugwise v0.16.9 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.9
  - Added schedule selector per thermostat using the new `select` platform.

## MAR 2022 [0.21.4]
- Smile:
  - Link to plugwise v0.16.8 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.8
  - Bugfixes via updating plugwise: 
    - Fix error when discovery IP resolving to IPv6 https://github.com/home-assistant/core/issues/68003
    - Refixing python-plugwise #158 

## MAR 2022 [0.21.3]
- Smile:
  - Link to plugwise v0.16.7 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.7
  - Introduce (not so) subtle hint that Anna shouldn't be installed when connected to an Adam #231
  - Fix python-plugwise #158 for systems with an Anna and Elga (w.r.t. outdoor temperature sensor)

## FEB 2022 [0.21.2]
- Smile:
  - Make homekit emulation an option (like scan-interval)
  - Make explicit that this is (most probably) non-core functionality
  - Reference for [scan_interval](https://github.com/home-assistant/core/pull/65808) ```If you need to customize the interval, you can do so by disabling automatic updates for the integration and using an automation to trigger homeassistant.update_entity service on your preferred interval.```

## FEB 2022 [0.21.1]
- Smile: 
  - Fix issue where notifications would cause an error (see issue #238)
  - Restore Homekit-functionality present in v0.20.1 and earlier versions

## FEB 2022 [0.21.0]
- Smile: refactor code following the coming HA Core update
  - Link to plugwise v0.16.6 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.6
  - Refactor code following the work done on the HA Core plugwise code, a big thank you to @Frenck!!
  - REMOVED: device_state sensor
  - ADDED: binary_sensors showing the heating and cooling (when cooling is present) states
  - Support Stretch with fw 2.7.18
  - Improve test scripting

## FEB 2022 [0.20.1]
- Smile:
  - Link to plugwise v0.16.2 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.2
  - Add support for Stretch with fw 2.7.18, via plugwise v0.16.2
  - Improve code: add basic typing

## JAN 2022 [0.20.0]
BREAKING: The Auxiliary device has been renamed to OpenTherm device, also there can be an OnOff device when there is an on-off type of heating-/cooling device connected to the Anna/Adam.
- Link to plugwise v0.16.1 - https://github.com/plugwise/python-plugwise/releases/tag/v0.16.1
- Fixes and improvements - via plugwise v0.16.1 (and v0.16.0)
- Smile Anna & Adam: 
  - Change to OpenTherm device, add an OnOff device when the Adam/Anna controls the connected device via on-off-control.
  - Add support for the latest Adam and Anna (beta) firmware
- Smile: 
  - Provide gateway-devices for Legacy Anna and Stretch
  - Implement full use of HA Core DataUpdateCoordinator functionality

## DEC 2021 [0.19.8]
- Smile Adam & Anna: add cooling-mode detection, presence and operation (fixes #171)
- Link to plugwise v0.15.7 - https://github.com/plugwise/python-plugwise/releases/tag/v0.15.7

## DEC 2021 [0.19.7]
- Update code to Core 2021.12 requirements

## NOV 2021 [0.19.6]
- Smile: 
  - Clean up and improve code
  - Bugfix via linking to plugwise v0.15.4 - https://github.com/plugwise/python-plugwise/releases/tag/v0.15.4
  - Fix test-code: don't use protected parameters

## Nov 2021 [v0.19.5]
- Refactor Smile-related code:
  - Implement Core `EntityDescription`-updates including `entity_category`.
- Link to plugwise v0.15.2 - https://github.com/plugwise/python-plugwise/releases/tag/v0.15.2
- Move testfixtures into tests/components/plugwise directory.
- Various test-related fixes.

## Nov 2021 [v0.19.0]
- Support new Core 2021.11 functionality: implement Visit Device button
- Bug fix: handle changing Smile IP (Core PR #58819)

## Oct 2021 [v0.18.2]
- Smile: adapt to HA Core platform-changes

## Oct 2021 [v0.18.1]

- Set minimal required version of Home Assistant core to 2021.9.0
- Stick: adapt to HA Core 2021.9 sensor-changes (Remove last_reset, use total_increasing instead) fixes issue #204

## Sept 2021 [v0.18.0]

- Link to plugwise v0.14.5 https://github.com/plugwise/python-plugwise/releases/tag/v0.14.5
- Smile: fully use the HA Core DataUpdateCoordinator, providing the smile-data in coordinator.data
- Smile: change state_class to "total" for interval- and net_cumulative sensors, remove all remnants of the last_reset-related code

##Sept 2021 [v0.17.9, v0.17.8, v0.17.7]
- Link to plugwise v0.14.2 https://github.com/plugwise/python-plugwise/releases/tag/v0.14.2
- Smile: adapt to HA Core 2021.9 sensor-changes (Remove last_reset, use total_increasing instead)

## Aug 2021 [v0.17.5]
- Link to plugwise v0.13.1 https://github.com/plugwise/python-plugwise/releases/tag/v0.13.1
- Smile: fully support legacy Smile P1 (specifically with firmware 2.1.13), fixing #187

## Aug 2021 [0.17.0]

- Link to plugwise v0.12.0 https://github.com/plugwise/python-plugwise/releases/tag/0.12.0
- Stick:
  - Feature: Add "Energy Consumption Today" sensor to allow adding devices to the new 'Energy' dashboard introduced in Home-Assistant 2021.8
  - Bugfix: Make energy consumption monitoring more reliable and possible fixes reported issues #149 & #157
- Smile:
  - Implement the new sensor attributes needed to support HA Core Energy
  - Correct the unit_of_measurement for cumulative energy sensors (Wh --> kWh)

## Jul 2021 [0.16.1]

- Link to plugwise v0.11.2 https://github.com/plugwise/python-plugwise/releases/tag/0.11.2
- Fix issue #183: config_flow looks different in Core 2021.7.0

## Jun 2021 [0.16.0]
- Link to plugwise v0.11.0 https://github.com/plugwise/python-plugwise/releases/tag/0.11.0
- Smile: 
  - add support for Plugwise Jip
  - bugfix: fix missing Tom/Floor climate-devices
## Jun 2021 [0.15.0]
- Link to plugwise v0.10.0 https://github.com/plugwise/python-plugwise/releases/tag/0.10.0
- Smile/Stretch: adapt to changes in plugwise v0.10.0 resulting in simpler/less code
## Jun 2021 [0.14.7]
- Stick: adapt to changed storage format of "system options" in HA 2021.6

## Apr 2021 [0.14.6]
- Link to plugwise v0.9.4 https://github.com/plugwise/python-plugwise/releases/tag/0.9.4
- Stick
  - Fix Issue #168
  - Fix a small bug in a LOG-message

## Mar 2021 [0.14.5]
- Smile/Stretch
  - Add lock-switches for Plugs, Circles, Stealths, etc.
  - Various small code improvements
  - Link to plugwise v0.9.3 https://github.com/plugwise/python-plugwise/releases/tag/0.9.3

## Febr 2021 [0.14.4]

- Smile/Stretch
  - Show more device information: manufacturer name, model name and firmware as available on the Smile/Stretch
  - Connect the heating_state for city heating to Adam and remove the Auxiliary device
  - Link to plugwise v0.9.2 https://github.com/plugwise/python-plugwise/releases/tag/0.9.2

## Febr 2021 [0.14.3]

- Smile
   - Add a DHW Comfort Mode switch (Feature Request)

## Jan 2021 [0.14.0]

- USB-Stick
  - New: Automatically accepting of joining request of new Plugwise devices if the `Enable newly added entries` system option is turned on (default). A notification will be popup after a new devices is joined.
  - Improved: For quicker response switch (relay) requests are handled with priority
  - Improved: Dynamically set the refresh interval based on the actual discovered devices with power measurement capabilities
  - Improved: Response messages received from Plugwise devices are now validated to their checksums.
  - Improved: Using the `device_remove` services will remove the devices from the device registry too.
  - Improved: Better handling of timeout issues and reduced communication messages.
  - Improved: Corrected log level assignments (debug, info, warning, errors)
  - Fixed: Missing power history values during last week of the month.
  - Fixed: Prevent a few rarely occurring communication failures.

## Oct 2020 [0.13.1]

The developer of the Plugwise Stick integration, @brefra, has joined the team. As a result we have added support for the Plugwise Stick.

## Sept 2020

- Add a service: plugwise.delete_notification, this allows you to dismiss a Plugwise Notification from HA Core.
- Support for switching groups created on the Plugwise App has been added, these are available on the Adam with Plugs and on the Stretch.
- Support for the Plugwise Stretch v2 and v3 has been added.

## Aug 2020

This custom_component can be installed to replace the HA Core Plugwise component. It can NO LONGER be installed next to the HA Core Plugwise component.
Due to this it behaves exactly as the HA Core Plugwise component: discovery works. But this beta-version has extra features and improvements!

PLEASE NOTE: ~~at the moment you will need to remove the existing Core Plugwise integration(s) before you install this beta custom_component. This is at the moment also needed when you want to return to using the Core Plugwise integration. When this is no longer needed, you can read about it here.~~ Since Core v0.115.0 this is no longer needed.

# What do we support (in short)?

- Thermostats
  - Adam (firmware 2.x and 3.x) and the accompanying Lisa's, Tom's, Floor's, Koen's and Plugs.
  - Anna (firmware 1.x, 3.x and 4.x)
  - Notifications for both types
- Power-related
  - Smile P1 (firmware 2.x, 3.x and 4.x)
  - Stretch (firmware 2.x and 3.x, legacy Circle's and Stealth's)
  - Stick (legacy Circle's, Stealth's and Scan's)

## What can I expect in HA Core from this component

- `climate`: A (number of) thermostat(s) visible in HA, including temperature, presets and heating-demand status, per thermostat. Also, setting of temperature, preset and switching the active schedule on and off. Cooling is only supported in combination with an Anna (fw 3.1 and 4.0).
- `sensor` and `binary_sensor`: A number of sensoric values depending on your hardware: outdoor temperature, Anna's illuminance, Tom's valve postion, Plug's and Circle/Stealth's power-values, P1 power- and gas-values, Plugwise Notifications.
- `switch`: The switch-parts of Plugs/Circles are available as switches, also switching them on/off is supported.

The `water_heater`-device present in previous releases has been replaced by an Auxiliary Device state-sensor. This sensor will only show up when there are more (than one) thermostats present in your climate-system.

# How to install?

- Use [HACS](https://hacs.xyz)
- Navigate to the `Integrations` page and use the three-dots icon on the top right to add a custom repository.
- Use the link to this page as the URL and select 'Integrations' as the category.
- Look for `Plugwise beta custom component` in `Integrations` and install it!

## How to add the integration to HA Core

For each Plugwise Smile (i.e. gateway) you will have to add it as an integration. For instance if you have an Adam and a Smile P1, you have to add them individually. If you have an Anna and an Adam, **do not add the Anna**, only add the Adam.

- [ ] In Home Assitant click on `Configuration`
- [ ] Click on `Integrations`
- [ ] You should see one or more discovered Smiles
- [ ] Click the `Configure` button and enter the Smile ID
- [ ] Click Add to see the magic happens

If there is no discovered Smile present or you are using the USB stick:

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

The config flow will then continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

## Options

Using the OPTIONS-button, the default Smile-data refresh-interval can be modified. There are no OPTIONS available for the Stick. The refresh interval of the devices connected to the Stick is automatically determined on the number of devices connecteda

# Frequently Asked Questions (FAQ)

## I don't like the name of the sensor or the icon

You can adjust these in `Configuration`, `Integration` -> `Entities` (e.g. `https://{Your HA address}/config/entities`)

Just click on the device and adjust accordingly!

Please note that you can also click the cogwheel right top corner to rename all entities of a device at once.

## It doesn't work

If you notice issues, we are on Discord and on the [Community forums](https://community.home-assistant.io/t/plugwise-core-and-custom-component/236250). You can also create an Issue in these repositories:

- [plugwise-beta](https://github.com/plugwise/plugwise-beta) - the `custom_component` for HA Core
- [python-plugwise](https://github.com/plugwise/python-plugwise) - the python module interfacing with the plugwise Smile or USB-stick

## Why 'Smile'?

We use the term Smile for the 'device connected to your home network', called Smile P1 for their power-meter, Smile if you have an Anna or Adam.

## Is it tested?

While we try to make sure that everything works as intended, we can't really test out changes happening to hardware devices. Our testing is done through testing against files from community members (see [python-plugwise tests](https://github.com/plugwise/python-plugwise/tree/main/tests)) and if you have a setup you are willing to share we highly welcome that. Just send us the files or submit a PR. Including your test code into the `tests/test_Smile.py` code is highly recommended.

Results of our tests are checked by Travis, click the left button (the one that should say 'Build passing' :)) on the [python-plugwise repository](https://github.com/plugwise/python-plugwise/).

## There is Plugwise / used to be Anna support in HA Core already?

**The former 'anna' support was replaced by the new Plugwise component, based on this beta-version.**

From the original sources by @laetificat it was improved upon and upstreamed by @CoMPaTech for Anna. Right after that @bouwew joined to improve and help maintain the code - as a result also Adam and P1 became supported. As of 2020 @brefra joined for the USB part(s) so we have a full range of Plugwise products supported.

As things like async were in high demand from HA Core, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Beta repository (accompanying the Plugwise python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module). Note that 'Plugwise-Smile' existed for a while before @brefra joined.

With the three combined forces we now support, maintain and improve on:

- `plugwise-beta` (this repository) for beta-testing new features to go into the `plugwise`-integration for HA
- [`python-plugwise`](https://github.com/plugwise/python-plugwise) for connecting to Plugwise products
- [`progress`](https://github.com/plugwise/progress) showing what are the differences between HA-core and this `custom_component` on https://plugwise.github.io/progress/

And yes anna-ha with haanna (to some degree) support Anna v1.8 - but they don't support Adam nor the Smile P1.
