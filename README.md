# Plugwise custom_component (BETA)

:warning::warning::warning: Always **read** the [release notes](https://github.com/plugwise/plugwise_usb-beta/releases) before upgrading, in case there are BREAKING changes! **Do note** the release title on alpha releases and only install them if specifically instructed by our team! :warning::warning::warning:

## About

A fully asynchronous approach to supporting Plugwise devices in Home-Assistant. This repository is **meant** for use of beta-testing. As of March 2021 we include testing against latest `dev` in Home-Assistant Core, the above batches should indicate compatibility and compliance.

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
[![Generic badge](https://img.shields.io/github/v/release/plugwise/plugwise_usb-beta)](https://github.com/plugwise/plugwise_usb-beta)

[![HASSfest](https://github.com/plugwise/plugwise_usb-beta/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/plugwise/plugwise_usb-beta/actions)
[![HA-Core](https://github.com/plugwise/plugwise_usb-beta/workflows/Test%20with%20HA-core/badge.svg)](https://github.com/plugwise/plugwise_usb-beta/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/plugwise/plugwise_usb-beta/main.svg)](https://results.pre-commit.ci/latest/github/plugwise/plugwise_usb-beta/main)

[![CodeFactor](https://www.codefactor.io/repository/github/plugwise/plugwise_usb-beta/badge)](https://www.codefactor.io/repository/github/plugwise/plugwise_usb-beta)

Always first attempt to use the native [Home Assistant](https://www.home-assistant.io/integrations/plugwise/)-component using this button

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

If you don't mind a bug now and then and are interested in helping us test new features and improvements, you can start using this BETA `custom_component`. We develop and maintain both versions.

## Required python module (status)

Our [`python-plugwise-usb`](https://github.com/plugwise/python-plugwise-usb) python module accompanies both the native and the `custom_component`. It's status is is:

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/plugwise)
[![PyPI version fury.io](https://badge.fury.io/py/plugwise.svg)](https://pypi.python.org/pypi/plugwise/)

[![Latest release](https://github.com/plugwise/python-plugwise-usb/workflows/Latest%20release/badge.svg)](https://github.com/plugwise/python-plugwise-usb/actions)
[![Newest commit](https://github.com/plugwise/python-plugwise-usb/workflows/Latest%20commit/badge.svg)](https://github.com/plugwise/python-plugwise-usb/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/plugwise/python-plugwise-usb/main.svg)](https://results.pre-commit.ci/latest/github/plugwise/python-plugwise-usb/main)

[![CodeFactor](https://www.codefactor.io/repository/github/plugwise/python-plugwise-usb/badge)](https://www.codefactor.io/repository/github/plugwise/python-plugwise-usb)
[![codecov](https://codecov.io/gh/plugwise/python-plugwise-usb/branch/main/graph/badge.svg)](https://codecov.io/gh/plugwise/python-plugwise-usb)

## Changelog

Our [Changelog](CHANGELOG.MD) is available as a [separate file](CHANGELOG.md) in addition to our commit-history.

## Usage

### What do we support (in short)?

- Power-related
  - Stick (legacy Circle's, Stealth's and Scan's)

#### USB notes

Up to spring of 2023 the `custom_component` `plugwise-beta` [plugwise-beta](https://github.com/plugwise/plugwise-beta/) supported both Networked and USB Plugwise products, as of that time we have split both the backend (python module) and the frontend into separate instances as per recent discussion with the Core team. The `plugwise` integration in HA Core (and therefore `plugwise-beta`) will remain supporting networked Plugwise products under an envisioned `plugwise_bv` Brand umbrella. This paves the way for this repository as upcoming `plugwise_usb-beta` `custom_integration` to being refactored and again upstream to HA Core (which was originally planned but there was no branding umbrella in Core back then).

As such we ask USB users, who are tied in with the `custom_component` as there is no Core integration available yet, for a little patience so we can split and refactor all repositories without loss of functionality for the end users. For our USB users that will however mean some **breaking changes** or customizing under the hood as the `custom_component` name will change and the appropriate naming in HA will do so accordingly. It is for the best though as this will ensure a way forward to HA Core integration, which has been our goal since starting to write Plugwise supporting code for Home Assistant.

### What can I expect in HA Core from this component

- `binary_sensor` and `sensor`: A number of sensoric values depending on your hardware: Plug's and Circle/Stealth's power-values.
- `switch`: The switch-parts of Plugs/Circles are available as switches, also switching them on/off is supported.

### How to install?

- Use [HACS](https://hacs.xyz)
- Navigate to the `Integrations` page and use the three-dots icon on the top right to add a custom repository.
- Use the link to this page as the URL and select 'Integrations' as the category.
- Look for `Plugwise beta custom component` in `Integrations` and install it!

#### How to add the integration to HA Core

If you are using the USB stick:

- [ ] Hit the `+` button in the right lower corner
- [ ] Search or browse for 'Plugwise USB' and click it

- [ ] Select or enter the USB-path
- [ ] Click SUBMIT and FINISH

The config flow will then continue to ask you if you want to put your Smile and detected other devices in area's and presto, things should be available to configure in lovelace.

## Frequently Asked Questions (FAQ)

### I don't like the name of the sensor or the icon

You can adjust these in `Configuration`, `Integration` -> `Entities` (e.g. `https://{Your HA address}/config/entities`)

Just click on the device and adjust accordingly!

Please note that you can also click the cogwheel right top corner to rename all entities of a device at once.

### It doesn't work

If you notice issues please create an issue in the appropriate repository, while we are on Discord and on the [Community forums](https://community.home-assistant.io/t/plugwise-core-and-custom-component/236250) this is not where we are actively checking for support requests.

- [plugwise_usb-beta](https://github.com/plugwise/plugwise_usb-beta/issues/new/choose) - the beta `custom_component` for HA Core we use for testing (also required for USB as Plugwise USB support is not available in Home Assistant Core yet).
- [python-plugwise-usb](https://github.com/plugwise/python-plugwise-usb/issues/new/choose) - the python module interfacing with the plugwise Smile or USB-stick

### Is it tested?

Disclaimer: Not yet (fully)

While we try to make sure that everything works as intended, we can't really test out changes happening to hardware devices. Our testing is done through testing against files from community members (see [python-plugwise-usb tests](https://github.com/plugwise/python-plugwise-usb/tree/main/tests)) and if you have a setup you are willing to share we highly welcome that. Just send us the files or submit a PR. Including your test code into the `tests/test_Smile.py` code is highly recommended.

Ensuring our commits work `scripts/core-testing.sh` will create a local clone of the Home Assistant Core dev-branch to test against. For full visibility of tests run this as `DEBUG=1 scripts/core-testing.sh` (or export DEBUG to something other than none). `pytest` will show full log by default when tests are failing.

Results of our tests are checked by GitHub Actions against Home Assistant (dev-branch), click the button 'Test with HA-core' in this repository or the 'Latest release'/'Latest commit' buttons on our [python-plugwise-usb repository](https://github.com/plugwise/python-plugwise-usb/).

### There is Plugwise / used to be Anna support in HA Core already?

**The former 'anna' support was replaced by the new Plugwise component, based on this beta-version.**

From the original sources by @laetificat it was improved upon and upstreamed by @CoMPaTech for Anna. Right after that @bouwew joined to improve and help maintain the code - as a result also Adam and P1 became supported. As of 2020 @brefra joined for the USB part(s) so we have a full range of Plugwise products supported.

As things like async were in high demand from HA Core, desired by the original author and a great challenge for us we rewrote it largely. The Plugwise Beta repository (accompanying the Plugwise python module) is intended for development purposes, just as `anna-ha` was for `haanna` (respectively the original before upstreaming and original python module). Note that 'Plugwise-Smile' existed for a while before @brefra joined.

With the three combined forces we now support, maintain and improve on:

- `plugwise-beta` (the network devices repository) for beta-testing new features to go into the Core `plugwise`-integration for HA
- [`python-plugwise`](https://github.com/plugwise/python-plugwise-usb) for connecting to Networked Plugwise products
- `plugwise_usb-beta` (this repository) for beta-testing new features to eventually go upstream to Core into the `plugwise_usb`-integration for HA
- [`python-plugwise-usb`](https://github.com/plugwise/python-plugwise-usb) for connecting to Plugwise products via USB
- [`progress`](https://github.com/plugwise/progress) showing what are the differences between HA-core and the network `custom_component` on [our progress page](https://plugwise.github.io/progress/) (marked as todo for this repo as well)

And yes anna-ha with haanna (to some degree) support Anna v1.8 - but they don't support Adam nor the Smile P1.
