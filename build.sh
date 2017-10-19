#!/bin/bash

cmd="$1"
PY_VERSION="python3.5"

# Paths
SCRIPT=$(readlink -f $0)
PROJPATH=`dirname $SCRIPT`
DEPS_DIR="$PROJPATH/deps"
PYENV_DIR="$PROJPATH/pyEnv"
LED_DIR="$DEPS_DIR/rpi_ws281x"

# Executables
INSTALL_PKG='apt-get install --assume-yes'
PYTHON="$PYENV_DIR/bin/$PY_VERSION"
PIP="$PYENV_DIR/bin/pip"

if [ "clean" = "$cmd" ]; then
	echo "CLEANING"
	echo ".... deleting deps ($DEPS_DIR)"
	rm -rf $DEPS_DIR
	echo ".... deleting pyenv ($PYENV_DIR)"
	rm -rf $PYENV_DIR
	echo ".... deleting runScript"
	rm run.sh
	exit
fi


#################################
## Install Packages
#################################

$INSTALL_PKG virtualenv scons $PY_VERSION-dev swig

#################################
## Create Virtual Env
#################################


if [ ! -d "./pyEnv" ]; then
	virtualenv -p /usr/bin/$PY_VERSION $PYENV_DIR
fi

#################################
## BuildDeps
#################################

if [ ! -d "$LED_DIR" ]; then
	echo "Installing Rpi_WS281X....."
	git clone https://github.com/jgarff/rpi_ws281x.git $LED_DIR
	scons -C $LED_DIR
	touch /etc/modprobe.d/snd-blacklist.conf
	echo "Blacklisting Kernel Module "
	echo "blacklist snd_bcm2835" > /etc/modprobe.d/snd-blacklist.conf

	pushd $LED_DIR/python
	$PYTHON setup.py install
	popd
	echo ".... Success"
fi

#################################
## Install Python Modules
#################################


#################################
## Generate Run Script
#################################

echo ".... Generate Run Script"
touch $PROJPATH/run.sh
echo "sudo $PYTHON $PROJPATH/src/rainbowraceway.py" > $PROJPATH/run.sh
chmod +x $PROJPATH/run.sh


echo "...Finished..."