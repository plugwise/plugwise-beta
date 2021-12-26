#!/bin/sh

# If you want to test a single file
# run as "scripts/core_testing.sh test_config_flow.py" or 
# "scripts/core_testing.sh test_sensor.py"
#
# if you fancy more options (i.e. show test results)
# run as "scripts/core_testing.sh test_config_flow.py -rP"

which python3.9 || ( echo "You should have python3.9 installed, or change the script yourself, exiting"; exit 1)
which git || ( echo "You should have git installed, exiting"; exit 1)

if [ ! -d ha-core ]; then
	echo ""
	echo "This script expects to be executed from the 'root' of the cloned plugwise-beta directory"
	echo "Then 'mkdir ha-core' and rerun this script (which will take some time, disk-space and prayers)"
	echo ""
	echo "Cowardly stopping now ... ow, and you *should* have python3.9 and virtualenv installed"
	echo ""
	echo "(this script largely resembles the 'Test with HA-core' action on github stored in .github/workflows/test.yml in the repo"
	echo ""
	exit 1
fi

# If only dir exists, but not cloned yet
if [ ! -f ha-core/requirements_test_all.txt ]; then
	echo ""
	echo " ** Cloning HA core **"
	echo ""
	git clone https://github.com/home-assistant/core.git ./ha-core
        if [ ! -f ha-core/requirements_test_all.txt ]; then
		echo ""
		echo "Cloning failed .. make sure ./ha-core exists and is an empty directory"
		echo ""
		echo "Stopping"
		echo ""
		exit 1
        fi
	cd ./ha-core
	echo ""
	echo " ** Resetting to dev **"
	echo ""
	git config pull.rebase true
	git checkout dev
	echo ""
	echo " ** Running setup scrvipt from HA core **"
	echo ""
        python3.9 -m venv venv
	script/setup
        . venv/bin/activate
	echo ""
	echo " ** Installing test requirements **"
	echo ""
        pip install -r requirements_test.txt
else
        cd ./ha-core
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
. venv/bin/activate
mkdir -p ./tmp
grep -hEi "pyroute2|sqlalchemy|zeroconf|pyserial|pytest-socket" requirements_test_all.txt requirements_test.txt > ./tmp/requirements_test_extra.txt
pip install -q --disable-pip-version-check -r ./tmp/requirements_test_extra.txt
pip install -q flake8
echo ""
echo "Checking manifest for current python-plugwise to install"
echo ""
pip install --disable-pip-version-check $(grep require ../custom_components/plugwise/manifest.json | cut -f 4 -d '"')
echo "plugwise version installed:"
echo "$(pip show plugwise | awk 'FNR <=2')"
echo ""
echo "Test commencing ..."
echo ""
pytest $2 --cov=homeassistant/components/plugwise/ --cov-report term-missing -- tests/components/plugwise/$1 && echo "" && echo "... flake8-ing ..." && flake8 homeassistant/components/plugwise/*py && echo "..." && flake8 tests/components/plugwise/*py && echo "... pylint-ing ..." && pylint homeassistant/components/plugwise/*py && echo "... black-ing ..." && black homeassistant/components/plugwise/*py tests/components/plugwise/*py
echo ""
echo "Copy back modified files ..."
echo ""
cp -r ./homeassistant/components/plugwise ../custom_components/
cp -r ./tests/components/plugwise ../tests/components/
deactivate

#        # disable for further figuring out, apparently HA doesn't pylint against test
#        #pylint tests/components/plugwise/*py
