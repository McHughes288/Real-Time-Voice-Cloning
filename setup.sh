#!/bin/bash

VENV=$HOME/venv_cloning
ROOT_CLONE=$HOME/git/voice_cloning

if [ ! -d $VENV ]; then
echo "Creating $VENV"
    virtualenv -p python3 $VENV
fi

echo "Starting venv..."
source $VENV/bin/activate

echo "Installing requirements..."
pip3 install -r $ROOT_CLONE/requirements.txt

if [ ! -f $ROOT_CLONE/inference/pretrained.zip ]; then
    echo "Downloading pretrained models..."
    gdown -O $ROOT_CLONE/inference/pretrained.zip https://drive.google.com/uc?id=1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc
    unzip $ROOT_CLONE/inference/pretrained.zip -d $ROOT_CLONE/inference
fi

mkdir -p $ROOT_CLONE/output




