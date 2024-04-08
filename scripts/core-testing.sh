#!/usr/bin/env bash
set -e

# By default assumes running against 'master' branch of Core-HA
# as requested by @bouwew for on-par development with the releases
# version of HA
#
# Override by setting HABRANCH environment variable to run against
# a different branch of core
#
# Github flows are run against both 'dev' and 'master'
core_branch="master"
if [ "x${BRANCH}" != "x" ]; then
	core_branch="${BRANCH}"
fi
echo "Working on HA-core branch ${core_branch}"

# If you want full pytest output run as
# DEBUG=1 scripts/core-testing.sh

# If you want to test a single file
# run as "scripts/core_testing.sh test_config_flow.py" or
# "scripts/core_testing.sh test_sensor.py"
#
# if you fancy more options (i.e. show test results)
# run as "scripts/core_testing.sh test_config_flow.py -rP"
#
# If you want to prepare for Core PR, run as
# "COMMIT_CHECK=true scripts/core_testing.sh"

# Which packages to install (to prevent installing all test requirements)
# actual package version ARE verified (i.e. grepped) from requirements_test_all
# separate packages with |
pip_packages="fnvhash|lru-dict|voluptuous|aiohttp_cors|pyroute2|sqlalchemy|zeroconf|pytest-socket|pre-commit|paho-mqtt|numpy|pydantic|ruff|ffmpeg|hassil"

echo ""
echo "Checking for necessary tools and preparing setup:"

which git || ( echo "You should have git installed, exiting"; exit 1)

which jq || ( echo "You should have jq installed, exiting"; exit 1)

# Cloned/adjusted code from python-plugwise, note that we don't actually
# use the 'venv', but instantiate it to ensure it works in the
# ha-core testing later on

# GITHUB ACTIONS $1
# - core_prep
# - pip_prep
# - testing
# - quality


my_path=$(git rev-parse --show-toplevel)

# Ensure environment is set-up
source "${my_path}/scripts/setup.sh"
# shellcheck disable=SC1091
source "${my_path}/scripts/python-venv.sh"

# i.e. args used for functions, not directions 
set +u
if [ -z "${GITHUB_ACTIONS}" ] ; then
	# Handle variables
	subject=""
	basedir=""
	if [ $# -eq 2 ]; then
		subject=$2
	fi
	if [ $# -gt 0 ]; then
		basedir=$1
	fi
fi

# Ensure ha-core exists
coredir="${my_path}/ha-core/"
manualdir="${my_path}/manual_clone_ha/"
mkdir -p "${coredir}"

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "core_prep" ] ; then 
	# If only dir exists, but not cloned yet
	if [ ! -f "${coredir}/requirements_test_all.txt" ]; then
		if [ -d "${manualdir}" ]; then
			echo ""
			echo " ** Re-using copy, rebasing and copy to HA core**"
			echo ""
			cd "${manualdir}" || exit
			echo ""
			git config pull.rebase true
			echo " ** Resetting to ${core_branch} (just cloned) **"
			git reset --hard || echo " - Should have nothing to reset to after cloning"
			git checkout "${core_branch}"
			echo ""
			cp -a "${manualdir}." "${coredir}"
		else
			echo ""
			echo " ** Cloning HA core **"
			echo ""
			git clone https://github.com/home-assistant/core.git "${coredir}"
			cp -a "${coredir}." "${manualdir}"
		fi
		if [ ! -f "${coredir}/requirements_test_all.txt" ]; then
			echo ""
			echo "Cloning failed .. make sure ${coredir} exists and is an empty directory"
			echo ""
			echo "Stopping"
			echo ""
			exit 1
		fi
		cd "${coredir}" || exit
		echo ""
		git config pull.rebase true
		echo " ** Resetting to ${core_branch} (just cloned) **"
		git reset --hard || echo " - Should have nothing to reset to after cloning"
		git checkout "${core_branch}"
	else
		cd "${coredir}" || exit
		echo ""
		echo " ** Resetting/rebasing core (re-using clone)**"
		echo ""
		# Always start from ${core_branch}, dropping any leftovers
		git stash || echo " - Nothing to stash"
		git stash drop -q || echo " - Nothing to stash drop"
		git clean -nfd || echo " - Nothing to clean up (show/dry-run)"
		git clean -fd || echo " - Nothing to clean up (clean)"
		git checkout "${core_branch}" || echo " - Already in ${core_branch}-branch"
		git branch -D fake_branch || echo " - No fake_branch to delete"
		# Force pull
		git config pull.rebase true
		git reset --hard
		git pull
	fi
	cd "${coredir}" || exit
	# Add tracker
	git log -1 | head -1 > "${coredir}/.git/plugwise-tracking"
	# Fake branch
	git checkout -b fake_branch

	echo ""
	echo "Ensure HA-core venv"
	# shellcheck disable=SC1091
	source "${my_path}/scripts/python-venv.sh"
        # shellcheck disable=SC1091
	source ./venv/bin/activate

	echo ""
	echo "Bootstrap pip parts of HA-core"
	grep -v "^#" "${coredir}/script/bootstrap" | grep "pip install" | sed 's/python3 -m pip install/uv pip install/g' | sh
	uv pip install -e . --config-settings editable_mode=compat --constraint homeassistant/package_constraints.txt

	echo ""
	echo "Cleaning existing plugwise from HA core"
	echo ""
	rm -r homeassistant/components/plugwise tests/components/plugwise || echo "already clean"
	echo ""
	echo "Overwriting with plugwise-beta"
	echo ""
	cp -r ../custom_components/plugwise ./homeassistant/components/
	cp -r ../tests/components/plugwise ./tests/components/
	echo ""
fi # core_prep

set +u
if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "pip_prep" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo "Ensure HA-core venv"
        # shellcheck disable=SC1091
        source "./venv/bin/activate"
	mkdir -p ./tmp
	echo ""
	echo "Ensure translations are there"
	echo ""
	python3 -m script.translations develop --all > /dev/null 2>&1
	echo ""
	echo "Ensure uv is there"
	echo ""
	python3 -m pip install pip uv
	echo ""
	echo "Installing pip modules (using uv)"
	echo ""
	echo " - HA requirements (core and test)"
	uv pip install --upgrade -r requirements.txt -r requirements_test.txt
	grep -hEi "${pip_packages}" requirements_test_all.txt > ./tmp/requirements_test_extra.txt
	echo " - extra's required for plugwise"
	uv pip install --upgrade -r ./tmp/requirements_test_extra.txt
	echo " - home assistant basics"
	uv pip install -e . --config-settings editable_mode=compat --constraint homeassistant/package_constraints.txt
	echo ""
	# When using test.py prettier makes multi-line, so use jq
	module=$(jq '.requirements[]' ../custom_components/plugwise/manifest.json | tr -d '"')
	#module=$(grep require ../custom_components/plugwise/manifest.json | cut -f 4 -d '"')
	echo "Checking manifest for current python-plugwise to install: ${module}"
	echo ""
	uv pip install --upgrade "${module}"
fi # pip_prep

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "testing" ] ; then 
	set +u
	cd "${coredir}" || exit
	echo ""
	echo "Ensure HA-core venv"
        # shellcheck disable=SC1091
        source "./venv/bin/activate"
	echo ""
	echo "Test commencing ..."
	echo ""
        debug_params=""
	if [ ! "${DEBUG}" == "" ] ; then 
        	debug_params="-rpP --log-cli-level=DEBUG"
	fi
	# shellcheck disable=SC2086
	pytest ${debug_params} ${subject} tests/components/plugwise/${basedir} --snapshot-update --cov=homeassistant/components/plugwise/ --cov-report term-missing || exit
fi # testing

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "quality" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo "Ensure HA-core venv"
        # shellcheck disable=SC1091
        source "./venv/bin/activate"
	echo ""
	set +e
	echo "... ruff-ing component..."
	ruff check --fix homeassistant/components/plugwise/*py || echo "Ruff applied autofixes"
	echo "... ruff-ing tests..."
	ruff check --fix tests/components/plugwise/*py || echo "Ruff applied autofixes"
	set -e
	echo "... mypy ..."
	script/run-in-env.sh mypy homeassistant/components/plugwise/*.py || exit
	cd ..
	echo "... markdownlint ..."
	pre-commit run --all-files --hook-stage manual markdownlint
fi # quality

# Copying back not necessary in actions
# hassfest is another action
if [ -z "${GITHUB_ACTIONS}" ]; then
	cd "${coredir}" || exit
	echo ""
	echo "Ensure HA-core venv"
        # shellcheck disable=SC1091
        source "./venv/bin/activate"
	echo ""
	echo "Copy back modified files ..."
	echo ""
	cp -r ./homeassistant/components/plugwise ../custom_components/
	cp -r ./tests/components/plugwise ../tests/components/
	echo "Removing 'version' from manifest for hassfest-ing, version not allowed in core components"
	echo ""
	# shellcheck disable=SC2090
	src_manifest="../custom_components/plugwise/manifest.json"
	dst_manifest="./homeassistant/components/plugwise/manifest.json"
        jq 'del(.version)' ${src_manifest} | tee ${dst_manifest}
	grep -q -E 'require.*http.*test-files.pythonhosted.*#' ./homeassistant/components/plugwise/manifest.json && (
	  echo "Changing requirement for hassfest pass ...."
	  # shellcheck disable=SC2090
	  sed -i".sedbck" 's/http.*test-files.pythonhosted.*#//g' ./homeassistant/components/plugwise/manifest.json
	)

	# Hassfest already runs on Github
	if [ -n "${GITHUB_ACTIONS}" ] ; then
		echo "Running hassfest for plugwise"
		python3 -m script.hassfest --requirements --action validate 
	fi
fi

# pylint was removed from 'quality' some time ago
# this is a much better replacement for actually checking everything
# including mypy
if [ -z "${GITHUB_ACTIONS}" ] && [ -n "${COMMIT_CHECK}" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo "Core PR pre-commit check ..."
	echo ""
        git add -A ; pre-commit
fi

if [ -z "${GITHUB_ACTIONS}" ] ; then 
	deactivate
fi

