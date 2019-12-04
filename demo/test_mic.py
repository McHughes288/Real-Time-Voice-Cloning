import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

fs=44100
duration = 5  # seconds
myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype='float64')
print("Recording Audio")
sd.wait()
print(myrecording.shape)
print(type(myrecording))
print("Audio recording complete , Play Audio")
# sd.play(myrecording, fs)
# sd.wait()
print("Play Audio Complete")