import json
import time
from datetime import datetime

import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import board
import busio
import librosa
import numpy as np
import requests
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play


class RaspberryPi:
    def __init__(self):
        self.lcd = None

    def initialise_lcd(self, lcd_columns=16, lcd_rows=2):
        print("Initialising lcd...")
        # Initialise I2C bus.
        i2c = busio.I2C(board.SCL, board.SDA)
        # Initialise the LCD class
        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
        self.lcd.clear()
        self.lcd.color = [100, 100, 100]

    def lcd_display(self, message, clear=True, scroll=False, t=None, blink=False):
        print(message)
        if self.lcd is not None:
            if clear:
                self.lcd.clear()
            self.lcd.blink = blink
            self.lcd.message = message
            if scroll:
                for i in range(len(message)):
                    time.sleep(0.2)
                    self.lcd.move_left()
                self.lcd.clear()
                self.lcd.message = message
            if t:
                time.sleep(t)
    
    def play_sound(self, wav_file):
        self.lcd_display("Playing audio...")
        audio = AudioSegment.from_wav(wav_file)
        play(audio.low_pass_filter(1000))


    def record_voice(self, duration, fs=44100):
        print("Recording voice...")
        # record voice for specified duration
        self.lcd_display("Speak into mic.\n Duration: %is" % duration)
        time.sleep(0.5)
        myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype="float32")
        for dur in range(duration-2, 0, -1):
            self.lcd_display("Speak into mic.\nTime left: %is" % dur, clear=False)
        sd.wait()

        # save file with timestamp
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H.%M.%S")
        rec_path = "output/recording_%s.wav" % date_time
        print("Saving recording %s..." % rec_path)
        librosa.output.write_wav(rec_path, myrecording, fs)

        return rec_path

    def predict_text_gpt2(self, gpt2_url, recording_path):
        self.lcd_display("Predicting text...\n using GPT2!")
        print(gpt2_url, recording_path)
        # TODO add David's container here!
        response = "The quick brown fox jumped over the lazy dog"
        return response

    def clone_voice(self, url, recording_path, text_to_synthesize):
        self.lcd_display("Cloning voice...\nand synthesizing text.")
        # send post request to voice cloning container
        response = requests.post(
            url,
            files={"audio": open(recording_path, 'rb')},
            data={"text": text_to_synthesize},
        )
        json_response = response.json()
        # get the data
        data = json.loads(json_response)["result"]
        cloned_voice = np.array(data["generated_voice"]).astype(np.float32)
        output_fs = data["sample_rate"]
        # save cloned voice
        output_path = recording_path.replace("recording", "output")
        librosa.output.write_wav(output_path, cloned_voice, output_fs)

        return output_path
    
    def reset(self):
        # clear lcd and turn off back light
        self.lcd.clear()
        self.lcd.color = [0, 0, 0]
