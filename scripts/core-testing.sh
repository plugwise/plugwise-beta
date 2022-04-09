#!/usr/bin/env bash
set -e

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
# seperate packges with |
pip_packages="fnvhash|lru-dict|voluptuous|aiohttp_cors|pyroute2|sqlalchemy|zeroconf|pyserial|pytest-socket|pre-commit"

echo ""
echo "Checking for neccesary tools and prearing setup:"

which git || ( echo "You should have git installed, exiting"; exit 1)

# Cloned/adjusted code from python-plugwise, note that we don't actually
# use the 'venv', but instantiate it to ensure it works in the
# ha-core testing later on

# GITHUB ACTIONS $1
# - core_prep
# - pip_prep
# - testing
# - quality


pyversions=("3.10" 3.9 dummy) # HA-Core is pinned to 3.9
my_path=$(git rev-parse --show-toplevel)
my_venv=${my_path}/venv

if [ -z "${GITHUB_ACTIONS}" ] ; then 
	# Ensures a python virtualenv is available at the highest available python3 version
	for pv in "${pyversions[@]};"; do
	    if [ "$(which "python$pv")" ]; then
		# If not (yet) available instantiate python virtualenv
		if [ ! -d "${my_venv}" ]; then
		    "python${pv}" -m venv "${my_venv}"
		    # Ensure wheel is installed (preventing local issues)
		    # shellcheck disable=SC1091
		    . "${my_venv}/bin/activate"
		fi
		break
	    fi
	done

	# shellcheck source=/dev/null
	. "${my_venv}/bin/activate"
	# shellcheck disable=2145
	which python3 || ( echo "You should have python3 (${pyversions[@]}) installed, or change the script yourself, exiting"; exit 1)
	python3 --version

	# Failsafe
	if [ ! -d "${my_venv}" ]; then
	    echo "Unable to instantiate venv, check your base python3 version and if you have python3-venv installed"
	    exit 1
	fi
	# /Cloned code
fi

# Skip targetting for github
# i.e. args used for functions, not directions 
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
mkdir -p "${coredir}"

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "core_prep" ] ; then 
	# If only dir exists, but not cloned yet
	if [ ! -f "${coredir}/requirements_test_all.txt" ]; then
		echo ""
		echo " ** Cloning HA core **"
		echo ""
		git clone https://github.com/home-assistant/core.git "${coredir}"
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
		echo " ** Resetting to dev **"
		echo ""
		git config pull.rebase true
		git checkout dev
		echo ""
		echo " ** Running setup script from HA core **"
		echo ""
		if [ -z "${GITHUB_ACTIONS}" ] ; then 
			# shellcheck source=/dev/null
			. "${my_path}/venv/bin/activate"
			python3 -m venv venv
		fi
		python3 -m pip install --upgrade pip 
		# Not a typo, core setup script resets back to pip 20.3
		script/setup || python3 -m pip install --upgrade pip 
		if [ -z "${GITHUB_ACTIONS}" ] ; then 
			# shellcheck source=/dev/null
			. venv/bin/activate
		fi
		echo ""
		echo " ** Installing test requirements **"
		echo ""
		pip install --upgrade -r requirements_test.txt
	else
		cd "${coredir}" || exit
		echo ""
		echo " ** Resetting/rebasing core **"
		echo ""
		# Always start from dev, dropping any leftovers
		git stash || echo " - Nothing to stash"
		git stash drop -q || echo " - Nothing in stash"
		git checkout dev || echo " - Already in dev-branch"
		git branch -D fake_branch || echo " - No fake_branch to delete"
		# Force pull
		git config pull.rebase true
		git reset --hard
		git pull
	fi
	# Add tracker
	git log -1 | head -1 > "${coredir}/.git/plugwise-tracking"
	# Fake branch
	git checkout -b fake_branch

	echo ""
	echo "Cleaning existing plugwise from HA core"
	echo ""
	rm -r homeassistant/components/plugwise tests/components/plugwise
	echo ""
	echo "Overwriting with plugwise-beta"
	echo ""
	cp -r ../custom_components/plugwise ./homeassistant/components/
	cp -r ../tests/components/plugwise ./tests/components/
	echo ""
	echo "Adding select to coveragerc as we don't mock this yet"
	echo ""
	sed -i".sedbck" 's#homeassistant/scripts/..py#homeassistant/components/plugwise/select.py#' .coveragerc
	echo ""
fi # core_prep

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "pip_prep" ] ; then 
	cd "${coredir}" || exit
	if [ -z "${GITHUB_ACTIONS}" ] ; then 
		echo "Activating venv and installing selected test modules (zeroconf,pyserial, etc)"
		echo ""
		# shellcheck source=/dev/null
		. venv/bin/activate
		echo ""
	fi
	python3 -m pip install -q --upgrade pip
	mkdir -p ./tmp
	echo ""
	echo "Installing pip modules"
	echo ""
	echo " - HA requirements (core and test)"
	pip install --upgrade -q --disable-pip-version-check -r requirements.txt -r requirements_test.txt
	grep -hEi "${pip_packages}" requirements_test_all.txt > ./tmp/requirements_test_extra.txt
	echo " - extra's required for plugwise"
	pip install --upgrade -q --disable-pip-version-check -r ./tmp/requirements_test_extra.txt
	echo " - flake8"
	pip install --upgrade -q flake8
	echo ""
	module=$(grep require ../custom_components/plugwise/manifest.json | cut -f 4 -d '"')
	echo "Checking manifest for current python-plugwise to install: ${module}"
	echo ""
	pip install --upgrade -q --disable-pip-version-check "${module}"
fi # pip_prep

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "testing" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo "Test commencing ..."
	echo ""
	# shellcheck disable=SC2086
	pytest ${subject} --cov=homeassistant/components/plugwise/ --cov-report term-missing -- "tests/components/plugwise/${basedir}" || exit
fi # testing

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "quality" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo "... flake8-ing component..."
	flake8 homeassistant/components/plugwise/*py || exit
	echo "... flake8-ing tests..."
	flake8 tests/components/plugwise/*py || exit
	echo "... black-ing ..."
	black homeassistant/components/plugwise/*py tests/components/plugwise/*py || exit
	# echo "... mypy ..."
	# script/run-in-env.sh mypy homeassistant/components/plugwise/*.py || exit
fi # quality

# Copying back not neccesary in actions
# hassfest is another action
if [ -z "${GITHUB_ACTIONS}" ]; then
	cd "${coredir}" || exit
	echo ""
	echo "Copy back modified files ..."
	echo ""
	cp -r ./homeassistant/components/plugwise ../custom_components/
	cp -r ./tests/components/plugwise ../tests/components/
	echo "Removing 'version' from manifest for hassfest-ing, version not allowed in core components"
	echo ""
	# shellcheck disable=SC2090
	sed -i".sedbck" '/version.:/d' ./homeassistant/components/plugwise/manifest.json
	grep -q -E 'require.*http.*test-files.pythonhosted.*#' ./homeassistant/components/plugwise/manifest.json && (
	  echo "Changing requirement for hassfest pass ...."
	  # shellcheck disable=SC2090
	  sed -i".sedbck" 's/http.*test-files.pythonhosted.*#//g' ./homeassistant/components/plugwise/manifest.json
	)
	echo "Running hassfest for plugwise"
	python3 -m script.hassfest --integration-path homeassistant/components/plugwise
fi

# pylint was removed from 'quality' some time ago
# this is a much better replacement for actually checking everything
# including isort and mypy
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

