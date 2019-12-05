import requests
import numpy as np
import json
import sounddevice as sd
recording_path = "/Users/John/Downloads/voices/john_mic2.wav"
text_to_synthesize = "This is a test from the rpi using a recorded voice."
response = requests.post(
    "http://code19.cantabresearch.com:8080/jobs",
    files={"audio": open(recording_path, 'rb')},
    data={"text": text_to_synthesize},
)
json_response = response.json()
data = json.loads(json_response)["result"]
cloned_voice = np.array(data["generated_voice"]).astype(np.float32)
output_fs = data["sample_rate"]
sd.play(cloned_voice, output_fs)
sd.wait()