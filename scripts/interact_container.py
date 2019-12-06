import requests
import numpy as np
import json
import sounddevice as sd
import librosa
from datetime import datetime 
import time

playback = False

duration = 5
fs = 16000
myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype="float32")
for dur in range(duration, 0, -1):
    print("Speak into mic. Time left: %is" % dur)
    time.sleep(1)
sd.wait()

if playback:
    print("Playback...")
    sd.play(myrecording, fs)
    sd.wait()

now = datetime.now()
date_time = now.strftime("%Y-%m-%d_%H.%M.%S")
rec_path = "output/recording_%s.wav" % date_time
print("Saving recording %s..." % rec_path)
librosa.output.write_wav(rec_path, myrecording, fs)

# rec_path = "/Users/johnh/git/voice_cloning/functests/data/johns_voice3.wav"

print("Cloning voice...")
text_to_synthesize = "The quick brown fox jumped over the lazy dog"
response = requests.post(
    "http://code19.cantabresearch.com:8080/jobs",
    files={"audio": open(rec_path, 'rb')},
    data={"text": text_to_synthesize},
)
json_response = response.json()
data = json.loads(json_response)["result"]
cloned_voice = np.array(data["generated_voice"]).astype(np.float32)
output_fs = data["sample_rate"]
librosa.output.write_wav("output/output_%s.wav" % date_time, cloned_voice, output_fs)
print(cloned_voice.shape)
if playback:
    print("Playing cloned voice...")
    sd.play(cloned_voice, output_fs)
    sd.wait()