#!/bin/bash

VENV=$HOME/venv_cloning
ROOT_CLONE=$HOME/git/Real-Time-Voice-Cloning

if [ ! -d $VENV ]; then
echo "Creating $VENV"
    virtualenv --system-site-packages -p python3 $HOME/venv_cloning
fi

echo "Starting venv..."
source ~/venv_cloning/bin/activate

echo "Installing requirements..."
pip3 install -r requirements_pi.txt

if [ ! -f $ROOT_CLONE/pretrained.zip ]; then
    echo "Downloading pretrained models..."
    gdown https://drive.google.com/uc?id=1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc
    unzip $ROOT_CLONE/pretrained.zip
    mkdir -p $ROOT_CLONE/output
    gdown https://drive.google.com/uc?id=1D3A5YSWiY-EnRWzWbzSqvj4YdY90wuXq
    pip3 install torch-1.0.0a0+8322165-cp37-cp37m-linux_armv7l.whl
fi

python3 demo_lcd.py




