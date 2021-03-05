#!/bin/sh

which python3.9 || ( echo "You should have python3.9 installed, or change the script yourself, exiting"; exit 1)
which git || ( echo "You should have git installed, exiting"; exit 1)

if [ ! -d ha-core ]; then
	echo ""
	echo "This script expects to be executed from the 'root' of the cloned plugwise-beta directory"
	echo "Then 'mkdir ha-core' and rerun this script (which will take some time, disk-space and prayers"
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
rm -r homeassistant/components/plugwise tests/fixtures/plugwise tests/components/plugwise
echo ""
echo "Overwriting with plugwise-beta"
echo ""
cp -r ../custom_components/plugwise ./homeassistant/components/
cp -r ../tests/fixtures/plugwise ./tests/fixtures/
cp -r ../tests/components/plugwise ./tests/components/
echo ""
echo "Activating venv and installing selected test modules (zeroconf,pyserial, etc)"
echo ""
. venv/bin/activate
mkdir ./tmp
egrep -i "sqlalchemy|zeroconf|pyserial" requirements_test_all.txt > ./tmp/requirements_test_extra.txt
pip install -r ./tmp/requirements_test_extra.txt
echo ""
echo "Checking manifest for current python-plugwise to install"
echo ""
pip install $(grep require ../custom_components/plugwise/manifest.json | cut -f 4 -d '"')
echo ""
echo "Test commencing ..."
echo ""
pytest --cov=homeassistant/components/plugwise/ --cov-report term-missing -- tests/components/plugwise/$1
deactivate

# Future, flake/pylint as well (not rewritten yet from test.yml workflow)
#        pip install flake8
#        flake8 homeassistant/components/plugwise/*py
#        flake8 tests/components/plugwise/*py
#        pylint homeassistant/components/plugwise/*py
#        # disable for further figuring out, apparently HA doesn't pylint against test
#        #pylint tests/components/plugwise/*py
