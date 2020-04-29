---
name: Bug report
about: Create a report to help us improve
title: "[BUG]"
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**Evidence**
1. Look for Errors related to plugwise-beta in Developer Tools --> Logs
2. If nothing found add the below to your `configuration.yaml` and restart HA

``` 
# Add/modify configuration.yaml
logger:
  default: warn
  logs:
    custom_components.plugwise-beta: debug
```

3. After the restart, at Developer Tools --> Logs, load the FULL HA LOG.
4. Upload relevant issues to a site like pastebin and copy the link here

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Home Assistant (please complete the following information):**
 - Version: [e.g. `0.108.2`]
 - Deployment: [e.g. 'raspberry/hassio' or 'py-venv']
 - Installed plugwise version: [e.g. 'plugwise-beta or HA-core']
 - Installed through [e.g. 'HACS', 'Core' or manual custom_component]

**Smile (please complete the following information):**
 - Sort of Smile: [e.g. Adam/Anna/P1]
 - Firmware: [check through the app or the integrations page in Home Assistant]

**Additional context**
Add any other context about the problem here.
