#!/usr/bin/env bash
set -eu

pyversions=(3.11 3.10 3.9)
my_path=$(git rev-parse --show-toplevel)
my_venv=${my_path}/venv

# Ensures a python virtualenv is available at the highest available python3 version
for pv in "${pyversions[@]};"; do
    if [ "$(which "python$pv")" ]; then
        # If not (yet) available instantiate python virtualenv
        if [ ! -d "${my_venv}" ]; then
            "python${pv}" -m venv "${my_venv}"
            # Ensure wheel is installed (preventing local issues)
            # shellcheck disable=SC1091
            . "${my_venv}/bin/activate"
            pip install wheel
        fi
        break
    fi
done

# Failsafe
if [ ! -d "${my_venv}" ]; then
    echo "Unable to instantiate venv, check your base python3 version and if you have python3-venv installed"
    exit 1
fi
