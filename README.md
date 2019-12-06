# voice_cloning

Hackamatics 2019 project

# Qucikstart
## Remote running
```bash
./scripts/build.sh
docker run -it --rm -p 8080:8080 docker-master.artifacts.speechmatics.io/voice_cloning:dba136 run_batch
curl -F "audio=@/home/johnh/git/voice_cloning/functests/data/johns_voice3.wav" -F text="This is a test from the batch api container using John's voice." http://localhost:8080/jobs > ~/git/voice_cloning/output/api_output.txt
```
## RPi running
ssh pi@192.168.128.217
```bash
cd $HOME/git/voice_cloning && ./scripts/setup-pi.sh
```
