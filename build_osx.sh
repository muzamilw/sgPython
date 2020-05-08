#!/usr/bin/env bash

PYTHON_VERSION="3.6.5"
PYTHON_EXEC_VERSION="python3.6"

# Change buildozer to use a python3.6 virtual environment instead of python2.7
pushd /usr/local/lib/$PYTHON_EXEC_VERSION/site-packages/buildozer
sed -i '' 's;virtualenv --python=python2.7;virtualenv --python=python3.6;g' __init__.py
popd

# Change the osx target to use python3 to run the package_app.py script.
pushd /usr/local/lib/$PYTHON_EXEC_VERSION/site-packages/buildozer/targets
sed -i '' "s;'python', 'package_app.py';'python3', 'package_app.py';g" osx.py
popd

# First run fails but is necessary to create the directory .buildozer
buildozer osx debug
if [[ "$?" != 0 ]]; then
    echo "[INFO] First run of buildozer failed as expected."
fi

# Go into the kivy sdk directory to create the file Kivy.app
pushd .buildozer/osx/platform/kivy-sdk-packager-master/osx
rm -Rf Kivy3.dmg
sed -i '' "s;3.5.0;$PYTHON_VERSION;g" create-osx-bundle.sh
sed -i '' "s;python3.5;$PYTHON_EXEC_VERSION;g" create-osx-bundle.sh
sed -i '' "s;rm {};rm -f {};g" create-osx-bundle.sh
./create-osx-bundle.sh python3
# Repair symlink
pushd Kivy.app/Contents/Resources/venv/bin/
rm ./python3
ln -s ../../../Frameworks/python/$PYTHON_VERSION/bin/python3 .
popd

# Go into kivy sdk directory and fix the script package_app.py to use the specified python version.
pushd .buildozer/osx/platform/kivy-sdk-packager-master/osx
sed -i '' "s;3.5.0;$PYTHON_VERSION;g" package_app.py
# Make it python3 compatible by removing decode(...) calls.
sed -i '' "s;\.decode('utf-8');;g" package_app.py
popd

popd

buildozer osx debug