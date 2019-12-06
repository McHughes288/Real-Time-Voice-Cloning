#!/bin/bash

VENV=$HOME/venv_pi
ROOT_CLONE=$HOME/git/voice_cloning

if [ ! -d $VENV ]; then
echo "Creating $VENV"
    virtualenv -p python3 $VENV
fi

echo "Starting venv..."
source $VENV/bin/activate

echo "Installing requirements..."

pip3 install --extra-index-url https://artifacts.speechmatics.io/speechmatics/api/pypi/pypi-master/simple -r $ROOT_CLONE/requirements-pi.txt

mkdir -p $ROOT_CLONE/output

python demo_pi.py