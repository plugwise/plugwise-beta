#!/usr/bin/env bash
set -e

# Add coloring
CNORM="\x1B[0m"   # normal
CFAIL="\x1B[31m"  # red
CINFO="\x1B[96m"  # cyan
CWARN="\x1B[93m"  # yellow

# Repository name (for reuse betweeh plugwise network and usb)
REPO_NAME="plugwise"

# By default assumes running against 'master' branch of Core-HA
# as requested by @bouwew for on-par development with the releases
# version of HA
#
# Override by setting BRANCH environment variable to run against
# a different branch of core
#
# Github flows are run against both 'dev' and 'master'
core_branch="master"
if [ "x${BRANCH}" != "x" ]; then
	core_branch="${BRANCH}"
fi
echo -e "${CINFO}Working on HA-core branch ${core_branch}${CNORM}"

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
pip_packages="fnvhash|lru-dict|voluptuous|aiohasupervisor|aiohttp_cors|pyroute2|sqlalchemy|zeroconf|pytest-socket|pre-commit|paho-mqtt|numpy|pydantic|ruff|ffmpeg|hassil|home-assistant-intents|pylint|pylint-per-file-ignores|cronsim"

echo ""
echo -e "${CINFO}Checking for necessary tools and preparing setup:${CNORM}"

which git || ( echo -e "${CFAIL}You should have git installed, exiting${CNORM}"; exit 1)

which jq || ( echo -e "${CFAIL}You should have jq installed, exiting${CNORM}"; exit 1)

# Cloned/adjusted code from python-${REPO_NAME}, note that we don't actually
# use the 'venv', but instantiate it to ensure it works in the
# ha-core testing later on

# GITHUB ACTIONS $1
# - core_prep
# - pip_prep
# - testing
# - quality

my_path=$(git rev-parse --show-toplevel)

# Ensure environment is set-up

# 20250613 Copied from HA-core and shell-check adjusted and modified for local use
set -e

if [ -z "$VIRTUAL_ENV" ]; then
  if [ -x "$(command -v uv)" ]; then
    uv venv --seed venv
  else
    python3 -m venv venv
  fi
  # shellcheck disable=SC1091 # ingesting virtualenv
  source venv/bin/activate
fi

if ! [ -x "$(command -v uv)" ]; then
  python3 -m pip install uv
fi
# /20250613

# Install commit requirements
uv pip install --upgrade pre-commit

# Install pre-commit hook
pre-commit install

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
			echo -e "${CINFO} ** Reusing copy, rebasing and copy to HA core**${CNORM}"
			echo ""
			cd "${manualdir}" || exit
			echo ""
			git config pull.rebase true
			echo -e "${CINFO} ** Resetting to ${core_branch} (just cloned) **${CNORM}"
			git reset --hard || echo -e "${CWARN} - Should have nothing to reset to after cloning${CNORM}"
			git checkout "${core_branch}"
			echo ""
			cp -a "${manualdir}." "${coredir}"
		else
			echo ""
			echo -e "${CINFO} ** Cloning HA core **${CNORM}"
			echo ""
			git clone https://github.com/home-assistant/core.git "${coredir}"
			cp -a "${coredir}." "${manualdir}"
		fi
		if [ ! -f "${coredir}/requirements_test_all.txt" ]; then
			echo ""
			echo -e "${CFAIL}Cloning failed .. make sure ${coredir} exists and is an empty directory${CNORM}"
			echo ""
			echo -e "${CINFO}Stopping${CNORM}"
			echo ""
			exit 1
		fi
		cd "${coredir}" || exit
		echo ""
		git config pull.rebase true
		echo -e "${CINFO} ** Resetting to ${core_branch} (just cloned) **${CNORM}"
		git reset --hard || echo -e "${CWARN} - Should have nothing to reset to after cloning${CNORM}"
		git checkout "${core_branch}"
	else
		cd "${coredir}" || exit
		echo ""
		echo -e "${CINFO} ** Resetting/rebasing core (reusing clone)**${CNORM}"
		echo ""
		# Always start from ${core_branch}, dropping any leftovers
		git stash || echo -e "${CWARN} - Nothing to stash${CNORM}"
		git stash drop -q || echo -e "${CWARN} - Nothing to stash drop${CNORM}"
		git clean -nfd || echo -e "${CWARN} - Nothing to clean up (show/dry-run)${CNORM}"
		git clean -fd || echo -e "${CWARN} - Nothing to clean up (clean)${CNORM}"
		git checkout "${core_branch}" || echo -e "${CWARN} - Already in ${core_branch}-branch${CNORM}"
		git branch -D fake_branch || echo -e "${CWARN} - No fake_branch to delete${CNORM}"
		# Force pull
		git config pull.rebase true
		git reset --hard
		git pull
	fi
	cd "${coredir}" || exit
	# Add tracker
	git log -1 | head -1 > "${coredir}/.git/${REPO_NAME}-tracking"
	# Fake branch
	git checkout -b fake_branch

	echo ""
	echo -e "${CINFO}Ensure HA-core venv${CWARN}"
        if [ -x "$(command -v uv)" ]; then
          uv venv --seed venv
        else
          python3 -m venv venv
        fi
        # shellcheck disable=SC1091
	source venv/bin/activate

	if ! [ -x "$(command -v uv)" ]; then
	  echo -e "${CINFO}Ensure uv presence${CWARN}"
	  python3 -m pip install uv
	fi

	echo -e "${CINFO}Bootstrap pip parts of HA-core${CWARN}"
	grep -v "^#" "${coredir}/script/bootstrap" | grep "pip install" | sed 's/python3 -m pip install/uv pip install/g' | sh
	uv pip install -e . --config-settings editable_mode=compat --constraint homeassistant/package_constraints.txt

	echo ""
	echo -e "${CINFO}Cleaning existing ${REPO_NAME} from HA core${CNORM}"
	echo ""
	rm -r homeassistant/components/${REPO_NAME} tests/components/${REPO_NAME} || echo -e "${CWARN}already clean${CNORM}"
	echo ""
	echo -e "${CINFO}Overwriting with ${REPO_NAME}-beta${CNORM}"
	echo ""
	cp -r ../custom_components/${REPO_NAME} ./homeassistant/components/
	cp -r ../tests/components/${REPO_NAME} ./tests/components/
	echo ""
fi # core_prep

set +u
if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "pip_prep" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo -e "${CINFO}Ensure HA-core venv${CNORM}"
        # shellcheck disable=SC1091
        source venv/bin/activate
	mkdir -p ./tmp
	echo ""
	echo -e "${CINFO}Ensure translations are there${CNORM}"
	echo ""
	python3 -m script.translations develop --all > /dev/null 2>&1
	echo ""
	if ! [ -x "$(command -v uv)" ]; then
	  echo -e "${CINFO}Ensure uv is there${CNORM}"
	  python3 -m pip install uv
	fi
	echo -e "${CINFO}Installing pip modules (using uv)${CNORM}"
	echo ""
	echo -e "${CINFO} - HA requirements (core and test)${CNORM}"
	uv pip install --upgrade -r requirements.txt -r requirements_test.txt
	grep -hEi "${pip_packages}" requirements_test_all.txt > ./tmp/requirements_test_extra.txt
	echo -e "${CINFO} - extra's required for ${REPO_NAME}${CNORM}"
	uv pip install --upgrade -r ./tmp/requirements_test_extra.txt
	echo -e "${CINFO} - home assistant basics${CNORM}"
	uv pip install -e . --config-settings editable_mode=compat --constraint homeassistant/package_constraints.txt
	echo ""
	# When using test.py prettier makes multi-line, so use jq
	module=$(jq '.requirements[]' ../custom_components/${REPO_NAME}/manifest.json | tr -d '"')
	#module=$(grep require ../custom_components/${REPO_NAME}/manifest.json | cut -f 4 -d '"')
	echo -e "${CINFO}Checking manifest for current python-${REPO_NAME} to install: ${module}${CNORM}"
	echo ""
	uv pip install --upgrade "${module}"
fi # pip_prep

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "testing" ] ; then 
	set +u
	cd "${coredir}" || exit
	echo ""
	echo -e "${CINFO}Ensure HA-core venv${CNORM}"
        # shellcheck disable=SC1091
        source venv/bin/activate
	echo ""
	echo -e "${CINFO}Test commencing ...${CNORM}"
	echo ""
        debug_params=""
	if [ ! "${DEBUG}" == "" ] ; then 
        	debug_params="-rpP --log-cli-level=DEBUG"
	fi
	# First test if snapshots still valid (silent fail, otherwise will update snapshots)
        PYTEST_COMMAND="pytest ${debug_params} ${subject} tests/components/${REPO_NAME}/${basedir} --cov=homeassistant/components/${REPO_NAME}/ --cov-report term-missing"
	eval "${PYTEST_COMMAND}" || {
		echo ""
        	echo -e "${CFAIL}Pytest / Snapshot validation failed, re-running to update snapshot ...${CNORM}"
		eval "${PYTEST_COMMAND} --snapshot-update" || {
		echo ""
        		echo -e "${CFAIL}Pytest failed, not a snapshot issue ...${CNORM}" || exit 1
		} && {
		echo ""
        		echo -e "${CINFO}Pytest / Snapshot validation passed"
		}
	} && {
		echo ""
        	echo -e "${CINFO}Pytest / Snapshot validation passed"
	}
fi # testing

if [ -z "${GITHUB_ACTIONS}" ] || [ "$1" == "quality" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo -e "${CINFO}Ensure HA-core venv${CNORM}"
        # shellcheck disable=SC1091
        source venv/bin/activate
	echo ""
	set +e
	echo -e "${CINFO}... ruff-ing component...${CNORM}"
	ruff check --fix homeassistant/components/${REPO_NAME}/*py || echo -e "${CWARN}Ruff applied autofixes${CNORM}"
	echo -e "${CINFO}... ruff-ing tests...${CNORM}"
	ruff check --fix tests/components/${REPO_NAME}/*py || echo -e "${CWARN}Ruff applied autofixes${CNORM}"
	set -e
	echo -e "${CINFO}... pylint-ing component...${CNORM}"
	pylint -j 0 --ignore-missing-annotations=y homeassistant/components/${REPO_NAME}/*py tests/components/${REPO_NAME}/*py || (echo -e "${CFAIL}Linting issue, exiting cowardly${CNORM}"; exit 1)
	echo -e "${CINFO}... mypy ...${CNORM}"
	script/run-in-env.sh mypy homeassistant/components/${REPO_NAME}/*.py || exit
	cd ..
	echo -e "${CINFO}... markdownlint ...${CNORM}"
	pre-commit run --all-files --hook-stage manual markdownlint
fi # quality

# Copying back not necessary in actions
# hassfest is another action
if [ -z "${GITHUB_ACTIONS}" ]; then
	cd "${coredir}" || exit
	echo ""
	echo "Ensure HA-core venv${CNORM}"
        # shellcheck disable=SC1091
        source venv/bin/activate
	echo ""
	echo -e "${CINFO}Copy back modified files ...${CNORM}"
	echo ""
	cp -r ./homeassistant/components/${REPO_NAME} ../custom_components/
	cp -r ./tests/components/${REPO_NAME} ../tests/components/
	echo -e "${CINFO}Removing 'version' from manifest for hassfest-ing, version not allowed in core components${CNORM}"
	echo ""
	# shellcheck disable=SC2090
	src_manifest="../custom_components/${REPO_NAME}/manifest.json"
	dst_manifest="./homeassistant/components/${REPO_NAME}/manifest.json"
        jq 'del(.version)' ${src_manifest} | tee ${dst_manifest}
	grep -q -E 'require.*http.*test-files.pythonhosted.*#' ./homeassistant/components/${REPO_NAME}/manifest.json && (
	  echo -e "${CINFO}Changing requirement for hassfest pass ....${CNORM}"
	  # shellcheck disable=SC2090
	  sed -i".sedbck" 's/http.*test-files.pythonhosted.*#//g' ./homeassistant/components/${REPO_NAME}/manifest.json
	)

	# Hassfest already runs on Github
	if [ -n "${GITHUB_ACTIONS}" ] ; then
		echo -e "${CINFO}Running hassfest for ${REPO_NAME}${CNORM}"
		python3 -m script.hassfest --requirements --action validate 
	fi
fi

# pylint was removed from 'quality' some time ago
# this is a much better replacement for actually checking everything
# including mypy
if [ -z "${GITHUB_ACTIONS}" ] && [ -n "${COMMIT_CHECK}" ] ; then 
	cd "${coredir}" || exit
	echo ""
	echo -e "${CINFO}Core PR pre-commit check ...${CNORM}"
	echo ""
        git add -A ; pre-commit
fi

if [ -z "${GITHUB_ACTIONS}" ] ; then 
	deactivate
fi

