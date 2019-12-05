#!/bin/bash -eux

# copy models
mkdir -p build/models
cp -fpv ./functests/models/encoder/saved_models/pretrained.pt build/models/encoder.pt
cp -fpva ./functests/models/synthesizer/saved_models/logs-pretrained/taco_pretrained build/models/synthesizer
cp -fpv ./functests/models/vocoder/saved_models/pretrained/pretrained.pt build/models/vocoder.pt
md5sum build/models/{encoder,vocoder}.pt > ./build/hashes
git rev-parse --short HEAD >> ./build/hashes

# build and push image
TAG=$(md5sum ./build/hashes | cut -c 1-6)
DOCKER_BUILDKIT=1 docker build --target app -t docker-master.artifacts.speechmatics.io/voice_cloning:${TAG} .