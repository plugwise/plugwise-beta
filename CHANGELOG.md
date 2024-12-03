# Changelog

Versions from 0.40 and up

## Ongoing

- Downstream Core PR #125178

## v0.55.2

- Link to plugwise [v1.6.2](https://github.com/plugwise/python-plugwise/releases/tag/v1.6.2), implementing Adam `control_state` related improvements.

## v0.55.1

- Bugfix for Issue #776
- Support python 3.13 / HA-Core 2024.12
- Link to plugwise [v1.6.1](https://github.com/plugwise/python-plugwise/releases/tag/v1.6.1)
- Make Config-OptionsFlow compatible with HA 2024.12.0

## v0.55.0

- **BREAKING change for Adam**: the existing device-based climate entities will be replaced by new zone-based climate entities, most likely with a different name.
- New Feature: implement zone-based climate entities for Adam, solving HA Core Issue [130597](https://github.com/home-assistant/core/issues/130597).
- Also new: add the provided zone sensors.
- Link to plugwise [v1.6.0](https://github.com/plugwise/python-plugwise/releases/tag/v1.6.0).

## v0.54.3

- Bugfix for #768 via plugwise [v1.5.2](https://github.com/plugwise/python-plugwise/releases/tag/v1.5.2).

## v0.54.2

- Link to plugwise [v1.5.1](https://github.com/plugwise/python-plugwise/releases/tag/v1.5.1) and adapt:
  - Change thermostat device-key `mode` to `climate_mode`

## v0.54.1

- Fix typing error
- Downstream Core PR #126896
- Optimize test code, improve docstrings and add comments

## v0.54.0

- Link to plugwise [v1.5.0](https://github.com/plugwise/python-plugwise/releases/tag/v1.5.0) and adapt:
  - Remove the connection-timeout function added in v0.53.3, not accepted in Core
  - Remove the need to pass a connection-timeout value to the backend library, as suggested by a Core dev
- Link to plugwise [v1.4.4](https://github.com/plugwise/python-plugwise/releases/tag/v1.4.4) and adapt
- Fix coordinator connection-method: don't use defaults

## v0.53.5

- Link to plugwise [v1.4.3](https://github.com/plugwise/python-plugwise/releases/tag/v1.4.3).

## v0.53.4

- Link to plugwise [v1.4.2](https://github.com/plugwise/python-plugwise/releases/tag/v1.4.2) solving #739.
- Improve / clean up config_flow code (#736 and #747).
- Typing and other fixes (#738).

## v0.53.3

- Test-code improvements.
- Fix errors showing after Core 2023.9.3 release.
- Set the connection-timeout based on the device discovered, 10s for actual devices, legacy devices require a 30s timeout.

## v0.53.2

- Climate-test: implement freezer.tick constructs.
- Implement Core PR [#126212](https://github.com/home-assistant/core/pull/126212)

## v0.53.1

- Show model_id for P1 gateway as well.
- Bump plugwise to [v1.4.0](https://github.com/plugwise/python-plugwise/releases/tag/v1.4.0)
- Add comment, small improvement.

## v0.53.0

- New Feature: show model_id's of all devices (Adam, Anna, not for legacy gateways).
- Bump plugwise to [v1.3.1](https://github.com/plugwise/python-plugwise/releases/tag/v1.3.1)

## v0.52.2

- Battery-state binary_sensors improvements via plugwise [v1.2.0](https://github.com/plugwise/python-plugwise/releases/tag/v1.2.0)
- Resolve depreciated use of accessing `hass.components.persistent_notification`.

## v0.52.1

- Downstream the latest Core Plugwise updates.
- Document code-differences vs Core Plugwise - parts for future upstreaming and parts that will not be downstreamed.
- Code improvements.

## v0.52.0

- Add battery-state binary_sensors for battery-powered devices via plugwise [v1.1.0](https://github.com/plugwise/python-plugwise/releases/tag/v1.1.0)
- Fix climate-test error: implement homeassistant.exceptions.ServiceValidationError

## v0.51.6

- Implement fix for [#677](https://github.com/plugwise/plugwise-beta/issues/677)

## v0.51.5

- Implement small coordinator-improvement from Core.
- Follow button-rework from Core.

## v0.51.4

- Refactor runtime-update/remove related code.
- Implement various new Core features.

## v0.51.3

- Implement fix for Core Issue #119686 via plugwise [v0.38.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.38.3)

## v0.51.2

- Bump plugwise to [v0.38.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.38.2)

## v0.51.1

- Bump plugwise to [v0.38.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.38.1)

## v0.51.0

- New Feature: Implemented a Reboot button to allow users to restart devices directly from Home Assistant, as requested in #604.
  Implemented via [plugwise v0.38.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.38.0)
- Reverted the redacting of diagnostics output, as it was not accepted in HA Core.

## v0.50.4

- Implement @plugwise_command for the Select platform via [plugwise v0.37.8](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.8) and [plugwise v0.37.9](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.9)

## v0.50.3

- Thermostat-schedule (Select) improvements via [plugwise v0.37.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.7)

## v0.50.2

- Fix for Core Issue [#117542](https://github.com/home-assistant/core/issues/117542)

## v0.50.1

- Code improvements via #640 (implement @plugwise_command for the Number platform) and #641

## v0.50.0

- Delete removed Plugwise devices at runtime.
- Follow backend fixture updates.
- Implement test for migration to secondary_boiler_state.

## v0.49.1

- Improve redacting in diagnostics.
- Fix for #629

## v0.49.0

- Add new Plugwise devices at runtime.

## v0.48.2

- Bugfix for #620 via [plugwise v0.37.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.3)
- Require python 3.12 (as Core 2024.2 already does)
- Link to plugwise v0.37.2 via [plugwise v0.37.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.2)
- Replace many recurring text-strings by CONSTANTS.

## v0.48.1

- Redact sensitive data in the diagnostics-download

## v0.48.0

- Add a delete-button per device, enables the user to manually delete a removed Plugwise device
- Add automatic deletion of removed Plugwise devices after a HA restart
- Replace outdated test-fixture, update related test-case.

## v0.47.4

- Link to plugwise v0.37.1 via [plugwise v0.37.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.1)

## v0.47.3

- Add off-icon for thermostat schedules.

## v0.47.2

- Add icons for the options of the Selects DHW mode, Gateway mode and Regulation mode.

## v0.47.1

- Implement Core PR's [#108498](https://github.com/home-assistant/core/pull/108498) and [#109464](https://github.com/home-assistant/core/pull/109464)
- Set minimum Core version to 2024.2.0

## v0.47.0

- Implement [plugwise v0.37.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.37.0)
  - The backend-code for actual and legacy Plugwise devices has been separated.
  - For actual devices xml-data is now only collected from /core/domain_objects.

## v0.46.3

- Don't use `api.devive-list`, create the list from the incoming PlugwiseData devices-dict.
- Remove the related `device_list.json` files.
- Remove the `notifications.json` files, the same data is present in the `all_data.json` files.

## v0.46.2

- Backend gateway_mode-related bugfixes via [plugwise v0.36.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.36.3).

## v0.46.1

- Improve support for Anna+Elga systems that do not support cooling via [plugwise v0.36.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.36.2).

## v0.46.0

- New Feature: for Adam, add the gateway_mode Select. This allows the user to set the Gateway Mode, options: Normal, Pause, Vacation.
  Implemented via [plugwise v0.36.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.36.1)
- Remove support for Adam with fw 2.x and Anna with fw 3.x, via [plugwise v0.35.4](https://github.com/plugwise/python-plugwise/releases/tag/v0.35.4).
- Fix [Core Issue #104433](https://github.com/home-assistant/core/issues/104433) via [plugwise v0.35.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.35.3)
- Implement [Core PR #104004](https://github.com/home-assistant/core/pull/104004)
- Implement [Core PR #104324](https://github.com/home-assistant/core/pull/104324)

## v0.45.0

- New feature: add an Off-option for the Thermostat-schedule Select, this option disables the schedule for the related thermostat.
- Fix not being able to turn a schedule off.
  Both updates implemented via [plugwise v0.35.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.35.1)

## v0.44.2

- Adam: return use of control_state, implement HAVCAction.PREHEATING. Fixing [Core Issue #103386](https://github.com/home-assistant/core/issues/103386)

## v0.44.1

- Bugfix: ensure selecting schedule works correctly

## v0.44.0

- New Feature: implement device_registry cleaning, solution to [Core Issue #102926](https://github.com/home-assistant/core/issues/102926)
- Revert entity_registry cleaning, not approved in Core

## v.0.43.1

- Anna + Elga improvements via [plugwise v0.34.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.34.3)

## v0.43.0

- New feature: for Adam, provide hvac_mode = off, related to the regulation_mode = off, next to the existing hvac_modes cool,
  heat and auto. Also, for Adam, return to providing a single setpoint for the heating and cooling modes.
  Implemented via [plugwise v0.34.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.34.0)

## v0.42.4

- Fix for [#501](https://github.com/plugwise/plugwise-beta/issues/501)

## v0.42.3

- Fix HA Core Issue #102204 via [plugwise v0.33.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.33.2)
- Remove use of control_state xml-key, via [plugwise v0.33.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.33.1)

## v0.42.2

- Revert incorrect zeroconf-changes

## v0.42.1

- Implement HA Core 2023.10.0 zeroconf-change
- Clean entity_registry when a Plugwise entity is removed / becomes orphaned

## v0.42.0

- Bugfixes and adding daily full-updating via [plugwise v0.33.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.33.0)
- Add number-tests, following Core PR [#100654](https://github.com/home-assistant/core/pull/100654)

### v0.41.4

- Link to [plugwise to v0.32.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.32.3)
- Improve NL-translations.
- Implement Core PR [#100008](https://github.com/home-assistant/core/pull/100008)

### v0.41.3

- test_diagnostics.py: line up with Core.
- Link to [plugwise v0.32.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.32.2)
- Correct the DeviceInfo import for Core 2023.9.0

### v0.41.2

- Link to [plugwise v0.32.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.32.1)
- Remove python3.9 compatibility: remove/replace all python3.9 references.
- Implement Ruff sorting fixes - tnx @CoMPaTech for achieving the line-up with the Core Plugwise code.
- Update p1v4_442_triple testfixture, adding a Plugwise notification for the Smile P1. Add a related testcase.
- Fix logging, line up for all platforms.
- More lining up with Core Plugwise, quality improvements.
- Test both versus core#dev- and core#master-branches.

### v0.41.1

- Line up with the latest Core Plugwise code.

### v0.41.0

- New Feature: add a temperature_offset Number for devices that support this function, via [plugwise v0.32.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.32.0)
- Correct the unit_of_measurement for the temperature_difference sensor.

### v0.40.6

- Typing improvements via [plugwise v0.31.9](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.9)
- Update fixtures and testfiles related to the updated plugwise backend version.
- Update and simplify number.py and select.py
- Add services entry to strings.json and translation files.

### v0.40.5

- Backend improvements via [plugwise v0.31.8](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.8),
  adapt to relevant changes as suggested in Core PR #[96915](https://github.com/home-assistant/core/pull/96915#discussion_r1269292691)
- Backend improvements via [plugwise v0.31.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.7), adapt to relevant changes.
- Implement improvements from PR's #93416, #96915
- Update anna_heatpump_heating test-fixture, update related test-function.

### v0.40.4

- Fix for [#417](https://github.com/plugwise/plugwise-beta/pull/424)
- Rename Jip sensor `relative_humidity` to `humidity` and migrate the unique_id.

### v0.40.3

- CI improvements, ruff over pylint, adhere to upstream ruff version.
- Fix Anna+Elga domestic_hot_water_setpoint-related bug via [plugwise v0.31.6](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.6)
- Cooling-related fix/improvements via [plugwise v0.31.5](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.5)
- Improvements via [plugwise v0.31.4](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.4)
- Copy improvements in typing and code from Core Plugiwse PR's #91769, #93162, #93345, #93371, #93375, #93416

### 0.40.2

- CI improvements
- Implement strict typing, also via [plugwise v0.31.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.31.3)
- Dynamic generated fixtures re-introduced.

### 0.40.1

- Smile(/Stretch) custom_component only - USB split off to [plugwise_usb-beta](https://github.com/plugwise/plugwise_usb-beta)

### 0.40.0

- More formal Split between Networked and USB code.
- Refactoring where necessary.

## Versions from 0.30 and up

### NEW APR 2023 [0.34.10] Implement latest Core PR's

- Core PR #[88967](https://github.com/home-assistant/core/pull/88967)
- Core PR #[90537](https://github.com/home-assistant/core/pull/90537)
- Implement name translations for sensors (translation_key)

## APR 2023 [0.34.9] Bugfixes for Stick and Anna + Elga

- Stick: 2nd fix for #369, merge PR #374 by @mvdwetering
- Final fix for #320 - via plugwise [v0.27.10](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.10)

### MAR 2023 [0.34.8] Bugfixes for Stick, P1 legacy

- Attempt to fix for reported Plugwise-Beta issue #347 - via plugwise [v0.27.8](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.8)
- Fix for #368 - via plugwise [v0.27.9](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.0)
- Fix for #369.
- Added pre-commit and additional linting (no or marginal code changes).
- Added tagging in #361 to enable a path forward for upstreaming (mostly isort and tagging, no or marginal code changes).
- Replacing flake8 linting with ruff as per upstream.

### FEB 2023 [0.34.7.1] Stick-bugfix, rename P1 gas-interval sensor, line up with Core Plugwise

- Sort manifest-json - [Core PR 87082](https://github.com/home-assistant/core/pull/87082)
- Link to plugwise module [v0.27.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.7)
- Implement moved EntityCategory
- Correct state_class to MEASUREMENT for all interval-sensors
- Remove unneeded state_class=MEASUREMENT, already set in PlugwiseSensorEntityDescription-class
- Implement Core PR 87449
- Implement `suggested_display_precision` for outdoor sensors
- Rename P1 sensor `gas_consumed_interval` to `gas_consumed_previous_hour gas_consumed_interval` and migrate
- Add pydantic to pip-packages, bump CACHE_VERSION to fix a test-enviroment error
- Implement [Core PR 87347](https://github.com/home-assistant/core/pull/87347)
- Implement [Core PR 87381](https://github.com/home-assistant/core/pull/87381)

### FEB 2023 [0.34.5] Fix various warnings

- Via plugwise module [v0.27.6](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.6)
- Adapt to HA Core [our #342](http://github.com/plugwise/plugwise-beta/pull/342)
- Correct various sensor attributes: PRs [#343](http://github.com/plugwise/plugwise-beta/pull/343) & [#344](http://github.com/plugwise/plugwise-beta/pull/344)

### JAN 2023 [0.34.4] Bugfix for #340

- Bugfix [#340](https://github.com/plugwise/plugwise-beta/issues/340) via plugwise [v0.27.5](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.5)

### JAN 2023 [0.34.3] Bump plugwise to v0.27.4

- Plugwise module [v0.27.4](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.4)
- Fix Temperature difference sensor, not a SensorDeviceClass.TEMPERATURE sensor

### JAN 2023 [0.34.2] Adapt to importing more Core UnitOf... enumerators

- Follow upstream [unit enumeration](https://developers.home-assistant.io/blog/2022/12/05/more-unit-enumerators)
- Implementation alternative for [Core PR 84386](https://github.com/home-assistant/core/pull/84386)

### JAN 2023 [0.34.1] Smile: save user input when adding the integration

### JAN 2023 [0.34.0] Implement Core Climate and Select translations

- Implement Core PRs [83286](https://github.com/home-assistant/core/pull/83286) and [84617](https://github.com/home-assistant/core/pull/84617)

### JAN 2023 [0.33.1] Bump plugwise to v0.27.1

- Plugwise module [v0.27.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.1)

### DEC 2022 [0.33.0] Smile P1: add support for 3-phase DMSR

- Add 3-phase support, this requires P1 firmware >= 4.4.2 - via plugwise module [v0.27.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.27.0)

### DEC 2022 [0.32.0] Update to Core 2022.12

- Implement [Core PR 82694](https://github.com/home-assistant/core/pull/82694)
- Implement `UnitOfTemperature` in `sensor.py`

### DEC 2022 [0.31.5] Bugfix

- Bugfix via plugwise module [v0.25.14](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.14)
- Improve number-detection so that it doesn't error on a sensor with the same name - fixing [Core Issue 83068](https://github.com/home-assistant/core/issues/83068)
- Add two new sensors: DHW setpoint and Maximum boiler temperature, these sensors can be present (not always) when they are not available as Numbers

### NOV 2022 [0.31.4] Bugfixes, improve exception-handling

- Bugfixes via plugwise module [v0.25.12](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.12)

### NOV 2022 [0.31.3] Thermostats: more improvements

- Anna+Elga: remove cooling-switch, add cooling_enabled binary_sensor (NOTE: reload integration every time the cooling-enabled switch position on the Elga is changed)
- Link to plugwise module [v0.25.10](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.10)
  - Fixes for [#240](https://github.com/plugwise/python-plugwise/issues/240), [Core Issue 81716](https://github.com/home-assistant/core/issues/81716), [Core Issue 81839](https://github.com/home-assistant/core/issues/81839), [Core Issue 81672](https://github.com/home-assistant/core/issues/81672) & [#241](https://github.com/plugwise/python-plugwise/issues/241)

### NOV 2022 not released [0.31.2] Bug-fixes

- Adam: hide cooling-related switch, binary_sensors when there is no cooling present, this fixes the unexpected appearance of new entities after the Adam 3.7.1 firmware-update.
- Properly handle an empty schedule, should fix #313
- Link to plugwise unreleased v0.25.9
- Link to plugwise unreleased v0.25.8

### NOV 2022 [0.31.1] Bugfix for Core issue #81531

- Fix wrong logic in plugwise module [v0.25.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.7)
- Fix bug via plugwise module [v0.25.6](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.6)
- Implement [Core PR 80722](https://github.com/home-assistant/core/pull/80722)

### OCT 2022 [0.31.0] Change to hvac_mode heat_cool, improvements and bugfixes

- Implement hvac_mode heat_cool for heating + cooling as required by HA Core
- Fix for plugwise/plugwise-beta #309 via plugwise module [v0.25.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.3)
- Fix heat_cool-related bug via plugwise module [v0.25.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.2)
- Link to plugwise module [v0.25.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.1)
- Link to plugwise module [v0.25.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.25.0)
- Fix for home-assistant/core#79708 via plugwise module [v0.24.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.24.1)
- Follow latest HA Core Plugwise changes

### OCT 2022 [0.30.1] Bugfix in plugwise module [v0.24.1]

- Plugwise module [v0.24.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.24.1)

### OCT 2022 [0.30.0] Improve support for Anna-Loria combination

- Enable Plugwise notifications for non-legacy Smile P1's
- Link to plugwise module [v0.24.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.24.0)

## Versions from 0.20 and up

### OCT 2022 [0.29.0] Non-legacy Smiles: introduce device availability

- Adam: Re-add vacation-preset (following change in the Plugwise App)
- Link to plugwise module [v0.23.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.23.0)

### Sept 2022 [0.28.0]

- Smile P1: change to two devices, rename/streamline device names and models - via plugwise module [v0.22.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.22.1)

### Sept 2022 [0.27.0]

- Implement [Core PR 75109](https://github.com/home-assistant/core/pull/75109) via plugwise module [v0.21.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.21.1)
- Implement [Core PR 75161](https://github.com/home-assistant/core/pull/75161)
- Climate: implementing the new Climate classes `ClimateEntityFeature`, `HVACAction`, and `HVACMode`.
- Climate: fix bug in `hvac_modes` determination, implement changes from plugwise module [v0.21.1
- Climate: `async_set_temperature()`: support `hvac_mode`-change
- Refresh test fixtures
- Adapt tests/asserts
- Adapt to recent DUC changes wrt error handling
- DUC: provide a single error-message (platinum requirement) when the connection is lost (a single return-message is not needed, provided by the DUC)
- Fix cooldown-interval is None at init, raise max. to 10 (max in Core)
- Follow [Core PR 76610](https://github.com/home-assistant/core/pull/76610) (link to plugwise module v0.21.3, simplify/revert cooling-related code)
- Implement [Core PR 78680](https://github.com/home-assistant/core/pull/78680)
- Implement [Core PR 78935](https://github.com/home-assistant/core/pull/78935)

### July 2022 [0.26.0]

- Smile: Add domestic_hot_water_setpoint Number, further fix cooling support.
  - Link to plugwise module [v0.21.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.21.0)
  - Add domestic_hot_water_setpoint Number, update/simplify number-set-value function.
  - Fix cooling support for Anna + Elga (user-tested).

### July 2022 [0.25.2b0]

- Smile: NumberEntity, config_flow test updates
  - Implement NumberEntity updates from Core
  - Implement FlowResultType in config_flow test [Core PR 74638](https://github.com/home-assistant/core/pull/74638)
  - HACS: bump minimum Core version to 2022.7.0

### July 2022 [0.25.1b0]

- Smile: fix/improve cooling support - via plugwise module [v0.20.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.20.1)

### June 2022 [0.25.0]

- Adam: add support for the Aqara Plug - via plugwise module [v0.20.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.20.0)

### June 2022 [0.24.2]

- Stick: fix async_get_registry warning in Core Log

### June 2022 [0.24.1]

- Smiles & Stretches: clean up & improve error handling/reporting
  - Link to plugwise module [v0.19.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.19.1)

### June 2022 [0.24.0]

- Smile Anna cooling-related updates
  - Link to plugwise module [v0.19.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.19.0)
  - For the Anna with Elga combination, add a CONFIGURE option `cooling on`. Select this option to let the Plugwise integration know that the cooling-feature of your Elga has been set to on.
  - Show `target_temp_high` and `target_temp_low` instead of `target_temperature`, when cooling is active, next to heating.
  - Add the `supported_features` as a property as they can change when the cooling-feature (on the Elga/Loria/Thermastage) is turned on or off.

### MAY 2022 [0.23.2]

- Smile bugfix: fixing [plugwise module 192](https://github.com/plugwise/python-plugwise/issues/192) and [Core Issue 72305](https://github.com/home-assistant/core/issues/72305)
  via plugwise module [v0.18.5)[https://github.com/plugwise/python-plugwise/releases/tag/v0.18.5]

### MAY 2022 [0.23.1]

- Smile: improve testcoverage, correct a small bug in climate.py

### MAY 2022 [0.23.0]

- Smile: rework & improve plugwise backend - via plugwise module [v0.18.0](https://github.com/plugwise/python-plugwise/releases/tag/v0.18.0)
  - Adam: don't show vacation-preset - via plugwise module [v0.18.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.18.1)
  - Fix handling of a connection-issue - via plugwise module [v0.18.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.18.2)
- Implement [Core PR 70975](https://github.com/home-assistant/core/pull/70975)
- Set coordinator cooldown time to 5.0 secs, this should allow for showing the correct climate status on the Core frontend after a manual change (in temperature setpoint, preset, schedule) after 5 seconds.
- Update number.py and select.py (add tests) based on review-feedback on changes in [Core PR 69210](https://github.com/home-assistant/core/pull/69210)
- Fix issues [#276](https://github.com/plugwise/plugwise-beta/issues/276) and [#280](https://github.com/plugwise/plugwise-beta/issues/280) - via plugwise module [v0.18.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.18.3)
- Speed up data collection - via plugwise module [v0.18.4](https://github.com/plugwise/python-plugwise/releases/tag/v0.18.4)
- Climate: move error-handling of set-functions to backend - via plugwise module v0.18.4
- Smile Anna & Adam: provide the Frontend refresh-interval as a settable parameter via the CONFIGURE button (1.5 to 5 seconds).
- Add tests for the select-platform.

### APR 2022 [0.22.4]

- Smile: Stretch bugfix, solving #277 via plugwise module [v0.17.8](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.8)

### APR 2022 [0.22.3]

- Smile:
  - Link to plugwise module [v0.17.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.7) and adapt to changes (fixtures, tests)
  - Add (back) compressor_state as binary_sensor (Anna - heat-pump)
  - Implement HA [Core PR 70366](https://github.com/home-assistant/core/pull/70366) fixing connectivity issues (should also fix issues #268, #274)
  - Improvements in climate-code

### APR 2022 [0.22.2]

- Smile:
  - Climate: filter/report invalid options when using the HA climate service functions
  - Climate: improve generation of the hvac_modes list:
    - Improve support for the cooling implementations of the Adam (manual) and the Anna (automatic)
    - Make hvac_modes a property as the contents of the hvac_modes list isn't fixed
  - Integration: fix CONFIGURE options not working

### APR 2022 [0.22.1]

- Smile:
  - Link to plugwise module [v0.17.6](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.6)
  - Link to plugwise module [v0.17.5](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.5)
  - Link to plugwise module [v0.17.3](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.3)
  - Implement [Core PR 69094](https://github.com/home-assistant/core/pull/69094)
  - Code improvements based on HA Core 2022.4.0

### MAR 2022 [0.22.0]

- Smile:
  - Link to plugwise module [v0.17.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.1), fixing [Core issue 68621](https://github.com/home-assistant/core/issues/68621)
  - Link to plugwise module [v0.17.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.17.2)
  - Rework select.py, add selector for the heating/cooling-system regulation mode.
  - Add number.py (and tests), provide an option for changing the maximum boiler (water) temperature setpoint.
  - Remove climate schedule attributes, moved to the options-attribute of the select schedule entity.
  - Implement fix for the sticking HA persistent notifications
  - Only show HVAC_MODE off for HomeKit emulation

### MAR 2022 [0.21.5]

- Smile:
  - **BREAKING** improved naming of the locally present outdoor temp sensor connected to the OpenTherm device: `outdoor_air_temperature`. The former `sensor.opentherm_outdoor_temperature` is now visible as `sensor.opentherm_outdoor_air_temperature`. Use of the zipcode based `outdoor_temperature` has not changed.
  - **POTENTIALLY BREAKING** for consistency renamed schema to schedule, i.e. the attributes will now be `available_schedules` and `selected_schedule`.
  - Link to plugwise module [v0.16.9](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.9)
  - Added schedule selector per thermostat using the new `select` platform.

### MAR 2022 [0.21.4]

- Smile:
  - Link to plugwise module [v0.16.8](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.8)
  - Bugfixes via updating plugwise:
    - Fix error when discovery IP resolving to IPv6 [Core Issue 68003](https://github.com/home-assistant/core/issues/68003)
    - Refixing python-plugwise #158

### MAR 2022 [0.21.3]

- Smile:
  - Link to plugwise module [v0.16.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.7)
  - Introduce (not so) subtle hint that Anna shouldn't be installed when connected to an Adam #231
  - Fix python-plugwise #158 for systems with an Anna and Elga (w.r.t. outdoor temperature sensor)

### FEB 2022 [0.21.2]

- Smile:
  - Make homekit emulation an option (like scan-interval)
  - Make explicit that this is (most probably) non-core functionality
  - Reference for [Core PR 65808 / `scan_interval`](https://github.com/home-assistant/core/pull/65808) `If you need to customize the interval, you can do so by disabling automatic updates for the integration and using an automation to trigger homeassistant.update_entity service on your preferred interval.`

### FEB 2022 [0.21.1]

- Smile:
  - Fix issue where notifications would cause an error (see issue #238)
  - Restore Homekit-functionality present in v0.20.1 and earlier versions

### FEB 2022 [0.21.0]

- Smile: refactor code following the coming HA Core update
  - Link to plugwise module [v0.16.6](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.6)
  - Refactor code following the work done on the HA Core plugwise code, a big thank you to @Frenck!!
  - REMOVED: device_state sensor
  - ADDED: binary_sensors showing the heating and cooling (when cooling is present) states
  - Support Stretch with fw 2.7.18
  - Improve test scripting

### FEB 2022 [0.20.1]

- Smile:
  - Link to plugwise module [v0.16.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.2)
  - Add support for Stretch with fw 2.7.18, via plugwise module [v0.16.2
  - Improve code: add basic typing

### JAN 2022 [0.20.0]

**BREAKING**: The Auxiliary device has been renamed to OpenTherm device, also there can be an OnOff device when there is an on-off type of heating-/cooling device connected to the Anna/Adam.

- Link to plugwise module [v0.16.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.16.1)
- Fixes and improvements - via plugwise module v0.16.1 (and v0.16.0)
- Smile Anna & Adam:
  - Change to OpenTherm device, add an OnOff device when the Adam/Anna controls the connected device via on-off-control.
  - Add support for the latest Adam and Anna (beta) firmware
- Smile:
  - Provide gateway-devices for Legacy Anna and Stretch
  - Implement full use of HA Core DataUpdateCoordinator functionality

## Versions from 0.10 and up

### DEC 2021 [0.19.8]

- Smile Adam & Anna: add cooling-mode detection, presence and operation (fixes #171)
- Link to plugwise module [v0.15.7](https://github.com/plugwise/python-plugwise/releases/tag/v0.15.7)

### DEC 2021 [0.19.7]

- Update code to Core 2021.12 requirements

### NOV 2021 [0.19.6]

- Smile:
  - Clean up and improve code
  - Bugfix via linking to plugwise module [v0.15.4](https://github.com/plugwise/python-plugwise/releases/tag/v0.15.4)
  - Fix test-code: don't use protected parameters

### Nov 2021 [v0.19.5]

- Refactor Smile-related code:
  - Implement Core `EntityDescription`-updates including `entity_category`.
- Link to plugwise module [v0.15.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.15.2)
- Move testfixtures into tests/components/plugwise directory.
- Various test-related fixes.

### Nov 2021 [v0.19.0]

- Support new Core 2021.11 functionality: implement Visit Device button
- Bug fix: handle changing Smile IP [Core PR 58819](https://github.com/home-assistant/core/pull/58819)

### Oct 2021 [v0.18.2]

- Smile: adapt to HA Core platform-changes

### Oct 2021 [v0.18.1]

- Set minimal required version of Home Assistant core to 2021.9.0
- Stick: adapt to HA Core 2021.9 sensor-changes (Remove last_reset, use total_increasing instead) fixes issue #204

### Sept 2021 [v0.18.0]

- Link to plugwise module [v0.14.5](https://github.com/plugwise/python-plugwise/releases/tag/v0.14.5)
- Smile: fully use the HA Core DataUpdateCoordinator, providing the smile-data in coordinator.data
- Smile: change state_class to "total" for interval- and net_cumulative sensors, remove all remnants of the last_reset-related code

### Sept 2021 [v0.17.9, v0.17.8, v0.17.7]

- Link to plugwise module [v0.14.2](https://github.com/plugwise/python-plugwise/releases/tag/v0.14.2)
- Smile: adapt to HA Core 2021.9 sensor-changes (Remove last_reset, use total_increasing instead)

### Aug 2021 [v0.17.5]

- Link to plugwise module [v0.13.1](https://github.com/plugwise/python-plugwise/releases/tag/v0.13.1)
- Smile: fully support legacy Smile P1 (specifically with firmware 2.1.13), fixing #187

### Aug 2021 [0.17.0]

- Link to plugwise module [v0.12.0](https://github.com/plugwise/python-plugwise/releases/tag/0.12.0)
- Stick:
  - Feature: Add "Energy Consumption Today" sensor to allow adding devices to the new 'Energy' dashboard introduced in Home-Assistant 2021.8
  - Bugfix: Make energy consumption monitoring more reliable and possible fixes reported issues #149 & #157
- Smile:
  - Implement the new sensor attributes needed to support HA Core Energy
  - Correct the unit_of_measurement for cumulative energy sensors (Wh --> kWh)

### Jul 2021 [0.16.1]

- Link to plugwise module [v0.11.2](https://github.com/plugwise/python-plugwise/releases/tag/0.11.2)
- Fix issue #183: config_flow looks different in Core 2021.7.0

### Jun 2021 [0.16.0]

- Link to plugwise module [v0.11.0](https://github.com/plugwise/python-plugwise/releases/tag/0.11.0)
- Smile:
  - add support for Plugwise Jip
  - bugfix: fix missing Tom/Floor climate-devices

### Jun 2021 [0.15.0]

- Link to plugwise module [v0.10.0](https://github.com/plugwise/python-plugwise/releases/tag/0.10.0)
- Smile/Stretch: adapt to changes in plugwise module v0.10.0 resulting in simpler/less code

### Jun 2021 [0.14.7]

- Stick: adapt to changed storage format of "system options" in HA 2021.6

### Apr 2021 [0.14.6]

- Link to plugwise module [v0.9.4](https://github.com/plugwise/python-plugwise/releases/tag/0.9.4)
- Stick
  - Fix Issue #168
  - Fix a small bug in a LOG-message

### Mar 2021 [0.14.5]

- Smile/Stretch
  - Add lock-switches for Plugs, Circles, Stealths, etc.
  - Various small code improvements
  - Link to plugwise module [v0.9.3](https://github.com/plugwise/python-plugwise/releases/tag/0.9.3)

### Febr 2021 [0.14.4]

- Smile/Stretch
  - Show more device information: manufacturer name, model name and firmware as available on the Smile/Stretch
  - Connect the heating_state for city heating to Adam and remove the Auxiliary device
  - Link to plugwise module [v0.9.2](https://github.com/plugwise/python-plugwise/releases/tag/0.9.2)

### Febr 2021 [0.14.3]

- Smile
  - Add a DHW Comfort Mode switch (Feature Request)

### Jan 2021 [0.14.0]

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

### Oct 2020 [0.13.1]

The developer of the Plugwise Stick integration, @brefra, has joined the team. As a result we have added support for the Plugwise Stick.

## Earlier versions

### Sept 2020

- Add a service: plugwise.delete_notification, this allows you to dismiss a Plugwise Notification from HA Core.
- Support for switching groups created on the Plugwise App has been added, these are available on the Adam with Plugs and on the Stretch.
- Support for the Plugwise Stretch v2 and v3 has been added.

#### Aug 2020

This custom_component can be installed to replace the HA Core Plugwise component. It can NO LONGER be installed next to the HA Core Plugwise component.
Due to this it behaves exactly as the HA Core Plugwise component: discovery works. But this beta-version has extra features and improvements!

PLEASE NOTE: ~~at the moment you will need to remove the existing Core Plugwise integration(s) before you install this beta custom_component. This is at the moment also needed when you want to return to using the Core Plugwise integration. When this is no longer needed, you can read about it here.~~ Since Core v0.115.0 this is no longer needed.
