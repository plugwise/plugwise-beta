#!/usr/bin/env bash
set -eu

my_path=$(git rev-parse --show-toplevel)

# shellcheck disable=SC1091
. "${my_path}/scripts/python-venv.sh"

# shellcheck disable=SC2154
if [ -f "${my_venv}/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "${my_venv}/bin/activate"
    # Install commit requirements
    pip install wheel
    pip install --upgrade -r requirements_commit.txt
    # Install pre-commit hook
    "${my_venv}/bin/pre-commit" install
else
    echo "Virtualenv available, bailing out"
    exit 2
fi
