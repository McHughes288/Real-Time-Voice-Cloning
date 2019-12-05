# voice_cloning

Hackamatics 2019 project

# Qucikstart
## Local running
```bash
make build
docker run -it --rm -p 8080:8080 docker-master.artifacts.speechmatics.io/voice_cloning:bca9eb run_batch
curl -F "file=@/home/johnh/git/voice_cloning/functests/data/johns_voice3.wav" -F text="This is a test from the batch api container using John's voice." http://localhost:8080/jobs
```