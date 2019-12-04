#!/bin/bash

VENV=$HOME/venv_cloning
ROOT_CLONE=$HOME/git/Real-Time-Voice-Cloning

if [ ! -d $VENV ]; then
    virtualenv -p python3 ~/venv_cloning
fi

source ~/venv_cloning/bin/activate

if [ ! -f $ROOT_CLONE/pretrained.zip ]; then
    pip install -r requirements.txt
    gdown https://drive.google.com/uc?id=1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc
    extract $ROOT_CLONE/pretrained.zip
    mkdir -p $ROOT_CLONE/output
fi

python3 demo_lcd




