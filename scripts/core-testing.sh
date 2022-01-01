#!/usr/bin/env bash
set -eu

# If you want to test a single file
# run as "scripts/core_testing.sh test_config_flow.py" or
# "scripts/core_testing.sh test_sensor.py"
#
# if you fancy more options (i.e. show test results)
# run as "scripts/core_testing.sh test_config_flow.py -rP"

echo ""
echo "Checking for neccesary tools and prearing setup:"

which git || ( echo "You should have git installed, exiting"; exit 1)

# Cloned/adjusted code from python-plugwise, note that we don't actually
# use the 'venv', but instantiate it to ensure it works in the
# ha-core testing later on


pyversions=(3.9 dummy) # HA-Core is pinned to 3.9
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

# Handle variables
subject=""
basedir=""
if [ $# -eq 2 ]; then
	subject=$2
fi
if [ $# -gt 0 ]; then
	basedir=$1
fi

# Handle sed on macos
sedmac=""
# shellcheck disable=SC2089
if [ "$(uname -s)" = "Darwin" ]; then sedmac="''"; fi

# Ensure ha-core exists
coredir="${my_path}/ha-core/"
mkdir -p "${coredir}"

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
	echo " ** Running setup scrvipt from HA core **"
	echo ""
	# shellcheck source=/dev/null
        . "${my_path}/venv/bin/activate"
        python3 -m venv venv
	script/setup
	# shellcheck source=/dev/null
        . venv/bin/activate
	echo ""
	echo " ** Installing test requirements **"
	echo ""
        pip install -r requirements_test.txt
else
        cd "${coredir}" || exit
	echo ""
	echo " ** Restting/rebasing core **"
	echo ""
        git config pull.rebase true
        git reset --hard
        git pull
fi


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
echo "Activating venv and installing selected test modules (zeroconf,pyserial, etc)"
echo ""
# shellcheck source=/dev/null
. venv/bin/activate
mkdir -p ./tmp
grep -hEi "pyroute2|sqlalchemy|zeroconf|pyserial|pytest-socket" requirements_test_all.txt requirements_test.txt > ./tmp/requirements_test_extra.txt
pip install -q --disable-pip-version-check -r ./tmp/requirements_test_extra.txt
pip install -q flake8
echo ""
echo "Checking manifest for current python-plugwise to install"
echo ""
pip install -q --disable-pip-version-check "$(grep require ../custom_components/plugwise/manifest.json | cut -f 4 -d '"')"
echo ""
echo "Test commencing ..."
echo ""
# shellcheck disable=SC2086
pytest ${subject} --cov=homeassistant/components/plugwise/ --cov-report term-missing -- "tests/components/plugwise/${basedir}" || exit
echo ""
echo "... flake8-ing component..."
flake8 homeassistant/components/plugwise/*py|| exit
echo "... flak8-ing tests..."
flake8 tests/components/plugwise/*py || exit
echo "... pylint-ing component ..."
pylint homeassistant/components/plugwise/*py || exit
echo "... black-ing ..."
black homeassistant/components/plugwise/*py tests/components/plugwise/*py || exit
echo ""
echo "Copy back modified files ..."
echo ""
cp -r ./homeassistant/components/plugwise ../custom_components/
cp -r ./tests/components/plugwise ../tests/components/
echo "Removing 'version' from manifest for hassfest-ing, version not allowed in core components"
echo ""
# shellcheck disable=SC2090
sed -i ${sedmac} '/version.:/d' ./homeassistant/components/plugwise/manifest.json
grep -q -E 'require.*http.*test-files.pythonhosted.*#' ./homeassistant/components/plugwise/manifest.json && (
  echo "Changing requirement for hassfest pass ...."
  # shellcheck disable=SC2090
  sed -i ${sedmac} 's/http.*test-files.pythonhosted.*#//g' ./homeassistant/components/plugwise/manifest.json
)
echo "Running hassfest for plugwise"
python3 -m script.hassfest --integration-path homeassistant/components/plugwise
deactivate

#        # disable for further figuring out, apparently HA doesn't pylint against test
#        #pylint tests/components/plugwise/*py
