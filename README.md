# Voice Cloning and Continuation with GPT-2

## Quickstart
### Remote server setup
```bash
./scripts/setup-server.sh
./scripts/build.sh
docker run -it --rm -p 8080:8080 docker-master.artifacts.speechmatics.io/voice_cloning:dba136 run_batch
curl -F "audio=@/home/johnh/git/voice_cloning/functests/data/johns_voice3.wav" -F text="This is a test from the batch api container using John's voice." http://localhost:8080/jobs > ~/git/voice_cloning/output/api_output.txt
```
### Raspberry pi setup
ssh pi@192.168.128.217
```bash
cd $HOME/git/voice_cloning && ./scripts/setup-pi.sh
```

## Project Description

This project was undertaken as part of an annual Speechmatics Hackathon known as "Hackamatics" in December 2019. The aim of the project was as follows: use under 10 seconds of speech spoken into a microphone to clone your voice; use the Speechmatics ASR engine to transribe what was said; feed the transcription into GPT-2 to predict a possible continuation; and finally this continuation would be played back in your synthesized voice. In other words, the final system, running on a Raspberry Pi, has the effect of completing a sentence for you with your tone of voice.

All of the inference work is done in containers running on a remote server. There are three containers used:
* Voice cloning - this takes a recorded wav file to synthesize and a string of text before returning the vocoded text (implemented in this repo)
* Speechmatics ASR - this takes the recorded wav and returns the text transcipt of what was said
* GPT-2 - this takes a string of text and predicts a possible coherent continuation

Another team in Hackamatics hooked up the Speechmatics ASR engine to GPT-2 while I focused on the voice cloning container and Raspberry Pi setup. Other than getting the voice cloning container to work, a script was written on the Raspberry Pi to tie everything together and make it interactive with the user in the real world. An Adafruit LCD screen displays instructions on when to record your voice with a hooked up microphone and buttons are used to let the user continue if they are happy. Once the voice is synthesised and GPT-2 has processed the transiption of what the user has said, the raspberry pi will play back the vocoded speech. This process takes around 20 seconds to complete.

Overall the project was a success with my work linking nicely with the other team. The only downside was the inference time and the pre-trained models not being that great at the cloning speech in noisy environments - the samples were biased towards american english and there were some clipping issues which caused artefacts in the audio. Bringing together speech synthesis and language modelling with GPT-2 was an extremely fun way to spend the 3 day hackathon.

## What this repo contains

Interesting files to look at are `./raspberry/pi.py`, `./demo_pi.py` and `apis/batch/controllers/batch_api.py`. Here is a description of the directory struture:

* `./apis/batch` contains the batch api configuration and the code that the voice cloning container runs when it is sent a file and a piece of text to generate.
* `./functests` functional test to ensure the batch api works as expected
* `./inference` contains voice cloning code from https://github.com/CorentinJ/Real-Time-Voice-Cloning
* `./raspberry` contains a raspberry pi class that deals with the peripherals such as the Adafruit lcd display, button presses, playing audio and recording audio. It also contains the code to interact with the voice cloning, Speechmatics and GPT-2 containers.
* `./scripts` setup scripts for the raspberry pi and server running the containers. In addition, there is the script to build the voice cloning container from the Dockerfile.
* `./demo_pi.py` is the main python file that runs the interactive loop. 
* `./run_batch` is the main entry point for the voice cloning container





