import json
import time
from datetime import datetime

import librosa
import numpy as np
import requests
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play

playback = True

duration = 6
fs = 16000
myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype="float32")
for dur in range(duration, 0, -1):
    print("Speak into mic. Time left: %is" % dur)
    time.sleep(1)
sd.wait()

# save recording
now = datetime.now()
date_time = now.strftime("%Y-%m-%d_%H.%M.%S")
rec_path = "output/recording_%s.wav" % date_time
print("Saving recording %s..." % rec_path)
librosa.output.write_wav(rec_path, myrecording, fs)

if playback:
    print("Playback...")
    rec = AudioSegment.from_wav(rec_path)
    play(rec)

# rec_path = "/Users/johnh/git/voice_cloning/functests/data/johns_voice3.wav"

print("Cloning voice...")
text_to_synthesize = "Once upon a time, three people decided to slay a big scary dragon"
response = requests.post(
    "http://code19.cantabresearch.com:8080/jobs",
    files={"audio": open(rec_path, 'rb')},
    data={"text": text_to_synthesize},
)
json_response = response.json()
data = json.loads(json_response)["result"]
cloned_voice = np.array(data["generated_voice"]).astype(np.float32)
output_fs = data["sample_rate"]

# save output
output_path = "output/output_%s.wav" % date_time
librosa.output.write_wav(output_path, cloned_voice, output_fs)
print(cloned_voice.shape)
if playback:
    print("Playing cloned voice...")
    output = AudioSegment.from_wav(output_path)
    play(output)
