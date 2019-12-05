import sounddevice as sd
import wavio
import numpy as np
import librosa

fs=16000
duration = 8  # seconds
myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype='float32')
print("Recording Audio")
sd.wait()

print("Play Audio")
sd.play(myrecording, fs)
sd.wait()

myrecording = np.squeeze(myrecording)
print(myrecording.shape)
print(type(myrecording[0]))

fpath="johns_voice3.wav"
librosa.output.write_wav(fpath, myrecording, fs) # needs float32
#wavio.write(fpath, myrecording, fs) # needs int32

print("Play Audio Complete")
