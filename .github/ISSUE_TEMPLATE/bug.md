name: Bug or problem.
description: Report an issue with Plugwise Beta.
title: "[BUG]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        This issue form is for reporting bugs only!

        If you have a feature or enhancement request, please use the appropriate [issue template][it].

        [it]: https://github.com/plugwise/plugwise-beta/issues/new/choose
  - type: textarea
    validations:
      required: true
    attributes:
      label: Describe the bug.
      description: >-
        Tell us what you were trying to do and what happened. Provide a clear and concise description of what the problem is.
  - type: markdown
    attributes:
      value: |
        ## Environment
  - type: input
    id: version
    validations:
      required: true
    attributes:
      label: What version of Home Assistant Core has the issue?
      placeholder: core-
      description: >
        Can be found in: [Configuration panel -> Info](https://my.home-assistant.io/redirect/info/).

        [![Open your Home Assistant instance and show your Home Assistant version information.](https://my.home-assistant.io/badges/info.svg)](https://my.home-assistant.io/redirect/info/)
  - type: input
    attributes:
      label: What was the last working version of Home Assistant Core?
      placeholder: core-
      description: >
        If known, otherwise leave blank.
  - type: dropdown
    validations:
      required: true
    attributes:
      label: What type of installation are you running?
      description: >
        Can be found in: [Configuration panel -> Info](https://my.home-assistant.io/redirect/info/).

        When selecting `Core`: remember to specify your way of running in the `additional information` textarea at the bottom, including your python version!

        [![Open your Home Assistant instance and show your Home Assistant version information.](https://my.home-assistant.io/badges/info.svg)](https://my.home-assistant.io/redirect/info/)
      options:
        - Home Assistant OS
        - Home Assistant Container
        - Home Assistant Supervised
        - Home Assistant Core
  - type: dropdown
    validations:
      required: true
    attributes:
      label: How did you install plugwise-beta?
      description: >
        You could be using the core-integration and just asked to leave feedback/improvements here, but more likely you installed either through HACS or manually as a `custom_component`.
        Feel free to select Core even if you are actually **not** using plugwise-beta, no problem, we gladly look into it to see if we can upstream it to Core eventually!

      options:
        - HACS
        - Manually installed `custom_component`
        - Cloned from GitHub
        - Home Assistant Core
