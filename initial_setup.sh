#!/bin/bash
VENV=$HOME/venv_cloning
ROOT_DIR=$HOME/git/Real-Time-Voice-Cloning
MODELS=${ROOT_DIR}/pretrained.zip

if [ ! -d "$VENV" ]; then
    echo "Creating $VENV"
    virtualenv -p python3 $VENV
fi

echo "Starting venv..."
source $VENV/bin/activate

if [ ! -f "$MODELS" ]; then
    echo "Installing requirements..."
    pip install -r ${ROOT_DIR}/requirements.txt
    echo "$MODELS does not exist, downloading..."
    gdown "https://drive.google.com/uc?id=1n1sPXvT34yXFLT47QZA6FIRGrwMeSsZc"
    extract ${ROOT_DIR}/pretrained.zip
    mv ${ROOT_DIR}/pretrained/encoder/saved_models ${ROOT_DIR}/encoder/saved_models
    mv ${ROOT_DIR}/pretrained/synthesizer/saved_models ${ROOT_DIR}/synthesizer/saved_models
    mv ${ROOT_DIR}/pretrained/vocoder/saved_models ${ROOT_DIR}/vocoder/saved_models
    rm -rf pretrained
    mkdir output
fi

python run_cloning.py



