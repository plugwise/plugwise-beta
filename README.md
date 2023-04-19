# Plugwise custom_component (BETA)

:warning::no_entry::warning: Do **not** use this custom_component for **USB**, this functionality has been moved to [plugwise_usb](https://github.com/plugwise/plugwise_usb-beta), see [why](#usb-notes) :warning::no_entry::warning:

:no_entry::no_entry::no_entry: If you have **no** intention to beta-test our integration, please defer to the **supported** release of this integration **natively** available in [Home Assistant](https://www.home-assistant.io/integrations/plugwise/)! :no_entry::no_entry::no_entry:

:warning::warning::warning: Always **read** the [release notes](https://github.com/plugwise/plugwise-beta/releases) before upgrading, in case there are BREAKING changes! **Do note** the release title on alpha releases and only install them if specifically instructed by our team! :warning::warning::warning:

## About

A fully asynchronous approach to supporting Plugwise devices in Home-Assistant. This repository is **meant** for use of beta-testing. As of March 2021 we include testing against latest `dev` in Home-Assistant Core, the above batches should indicate compatibility and compliance.

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
[![Generic badge](https://img.shields.io/github/v/release/plugwise/plugwise-beta)](https://github.com/plugwise/plugwise-beta)

[![HASSfest](https://github.com/plugwise/plugwise-beta/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/plugwise/plugwise-beta/actions)
[![HA-Core](https://github.com/plugwise/plugwise-beta/workflows/Test%20with%20HA-core/badge.svg)](https://github.com/plugwise/plugwise-beta/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/plugwise/plugwise-beta/main.svg)](https://results.pre-commit.ci/latest/github/plugwise/plugwise-beta/main)

[![CodeFactor](https://www.codefactor.io/repository/github/plugwise/plugwise-beta/badge)](https://www.codefactor.io/repository/github/plugwise/plugwise-beta)

Always first attempt to use the native [Home Assistant](https://www.home-assistant.io/integrations/plugwise/)-component using this button

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

If you don't mind a bug now and then and are interested in helping us test new features and improvements, you can start using this BETA `custom_component`. We develop and maintain both versions.

## Required python module (status)

Our [`python-plugwise`](https://github.com/plugwise/python-plugwise) python module accompanies both the native and the `custom_component`. It's status is is:

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
[![PyPI version fury.io](https://badge.fury.io/py/plugwise.svg)](https://pypi.python.org/pypi/plugwise/)

[![Latest release](https://github.com/plugwise/python-plugwise/workflows/Latest%20release/badge.svg)](https://github.com/plugwise/python-plugwise/actions)
[![Newest commit](https://github.com/plugwise/python-plugwise/workflows/Latest%20commit/badge.svg)](https://github.com/plugwise/python-plugwise/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/plugwise/python-plugwise/main.svg)](https://results.pre-commit.ci/latest/github/plugwise/python-plugwise/main)

[![CodeFactor](https://www.codefactor.io/repository/github/plugwise/python-plugwise/badge)](https://www.codefactor.io/repository/github/plugwise/python-plugwise)
[![codecov](https://codecov.io/gh/plugwise/python-plugwise/branch/main/graph/badge.svg)](https://codecov.io/gh/plugwise/python-plugwise)

## Changelog

Our [Changelog](CHANGELOG.MD) is available as a [separate file](CHANGELOG.md) in addition to our commit-history.

## Usage

### What do we support (in short)?

- Thermostats
  - Adam (firmware 2.x and 3.x) and the accompanying Lisa's, Tom's, Floor's, Koen's and Plugs.
  - Anna (firmware 1.x, 3.x and 4.x)
  - Notifications for both types
- Power-related
  - Smile P1 (firmware 2.x, 3.x and 4.x)
  - Stretch (firmware 2.x and 3.x, legacy Circle's and Stealth's)

Additional to the **Core** component we support Homekit emulation, notifications and changing some timing. This will not be upstreamed and is code that remained in our codebase (i.e. denied upstreaming by the Core Team for acceptable reasons though we have some people already using that (mostly by them requested) functionality).

#### USB notes

Up to spring of 2023 this `custom_component` supported both Networked and USB Plugwise products, as of that time we have split both the backend (python module) and the frontend into separate instances as per recent discussion with the Core team. The `plugwise` integration in HA Core (and therefore `plugwise-beta`) will remain supporting networked Plugwise products under an envisioned `plugwise_bv` Brand umbrella. This paves the way for the upcoming `plugwise_usb-beta` `custom_integration` to refactor and again upstream to HA Core (which was originally planned but there was no branding umbrella in Core back then).

As such we ask USB users, who are tied in with the `custom_component` as there is no Core integration available yet, for a little patience so we can split and refactor all repositories without loss of functionality for the end users. For our USB users that will however mean some **breaking changes** or customizing under the hood as the `custom_component` name will change and the appropriate naming in HA will do so accordingly. It is for the best though as this will ensure a way forward to HA Core integration, which has been our goal since starting to write Plugwise supporting code for Home Assistant.

### What can I expect in HA Core from this component

- `binary_sensor` and `sensor`: A number of sensoric values depending on your hardware: outdoor temperature, Anna's illuminance, Tom's valve position, Plug's and Circle/Stealth's power-values, P1 power- and gas-values, Plugwise Notifications.
- `climate`: A (number of) thermostat(s) visible in HA, including temperature, presets and heating-demand status, per thermostat. Also, setting of temperature, preset and switching the active schedule on and off. Cooling is only supported in combination with an Anna (fw 3.1 and 4.0).
- `number`: Numerical indication on boiler setpoints.
- `select`: Input selector to choose the active schedule.
- `switch`: The switch-parts of Plugs/Circles are available as switches, also switching them on/off is supported.

### How to install?

- Use [HACS](https://hacs.xyz)
- Navigate to the `Integrations` page and use the three-dots icon on the top right to add a custom repository.
- Use the link to this page as the URL and select 'Integrations' as the category.
- Look for `Plugwise beta custom component` in `Integrations` and install it!

#### How to add the integration to HA Core

For each Plugwise Smile (i.e. gateway) you will have to add it as an integration. For instance if you have an Adam and a Smile P1, you have to add them individually. If you have an Anna and an Adam, **do not add the Anna**, only add the Adam.

- [ ] In Home Assistant click on `Configuration`
- [ ] Click on `Integrations`
- [ ] You should see one or more discovered Smiles
- [ ] Click the `Configure` button and enter the Smile ID
- [ ] Click Add to see the magic happens

If there is no discovered Smile present:

- [ ] Hit the `+` button in the right lower corner
- [ ] Search or browse for 'Plugwise beta' and click it

- [ ] Enter your Smile IP-address and the 8 character ID of the smile
- [ ] Click SUBMIT and FINISH and hopefully the magic happens
- [ ] Repeat this process to add more Smiles

The config flow will then continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

#### Options

Using the OPTIONS-button, the default Smile-data refresh-interval can be modified. There are no OPTIONS available for the Stick. The refresh interval of the devices connected to the Stick is automatically determined on the number of devices connecteda

## Frequently Asked Questions (FAQ)

### I don't like the name of the sensor or the icon

You can adjust these in `Configuration`, `Integration` -> `Entities` (e.g. `https://{Your HA address}/config/entities`)

Just click on the device and adjust accordingly!

Please note that you can also click the cogwheel right top corner to rename all entities of a device at once.

### It doesn't work

If you notice issues please create an issue in the appropriate repository, while we are on Discord and on the [Community forums](https://community.home-assistant.io/t/plugwise-core-and-custom-component/236250) this is not where we are actively checking for support requests.

- [plugwise-beta](https://github.com/plugwise/plugwise-beta/issues/new/choose) - the beta `custom_component` for HA Core we use for testing (also required for USB as Plugwise USB support is not available in Home Assistant Core yet).
- [python-plugwise](https://github.com/plugwise/python-plugwise/issues/new/choose) - the python module interfacing with the plugwise Smile or USB-stick

### Why 'Smile'?

We use the term Smile for the 'device connected to your home network', called Smile P1 for their power-meter, Smile if you have an Anna or Adam.

### Is it tested?

While we try to make sure that everything works as intended, we can't really test out changes happening to hardware devices. Our testing is done through testing against files from community members (see [python-plugwise tests](https://github.com/plugwise/python-plugwise/tree/main/tests)) and if you have a setup you are willing to share we highly welcome that. Just send us the files or submit a PR. Including your test code into the `tests/test_Smile.py` code is highly recommended.

Ensuring our commits work `scripts/core-testing.sh` will create a local clone of the Home Assistant Core dev-branch to test against. For full visibility of tests run this as `DEBUG=1 scripts/core-testing.sh` (or export DEBUG to something other than none). `pytest` will show full log by default when tests are failing.

Results of our tests are checked by GitHub Actions against Home Assistant (dev-branch), click the button 'Test with HA-core' in this repository or the 'Latest release'/'Latest commit' buttons on our [python-plugwise repository](https://github.com/plugwise/python-plugwise/).

### There is Plugwise / used to be Anna support in HA Core already?

**The former 'anna' support was replaced by the new Plugwise component, based on this beta-version.**

From the original sources by @laetificat it was improved upon and upstreamed by @CoMPaTech for Anna. Right after that @bouwew joined to improve and help maintain the code - as a result also Adam and P1 became supported. As of 2020 @brefra joined for the USB part(s) so we have a full range of Plugwise products supported.

As things like async were in high demand from HA Core, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Beta repository (accompanying the Plugwise python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module). Note that 'Plugwise-Smile' existed for a while before @brefra joined.

With the three combined forces we now support, maintain and improve on:

- `plugwise-beta` (this repository) for beta-testing new features to go into the Core `plugwise`-integration for HA
- [`python-plugwise`](https://github.com/plugwise/python-plugwise-usb) for connecting to Networked Plugwise products
- `plugwise_usb-beta` (the USB repository) for beta-testing new features to eventually go upstream to Core into the `plugwise_usb`-integration for HA
- [`python-plugwise-usb`](https://github.com/plugwise/python-plugwise-usb) for connecting to Plugwise products via USB
- [`progress`](https://github.com/plugwise/progress) showing what are the differences between HA-core and the network `custom_component` on [our progress page](https://plugwise.github.io/progress/) (marked as todo for USB as well)

And yes anna-ha with haanna (to some degree) support Anna v1.8 - but they don't support Adam nor the Smile P1.
