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

import asyncio
from dataclasses import dataclass
from typing import List
import sys

import smwebsocket
import smwebsocket.client as client
import smwebsocket.models
from smwebsocket.models import ServerMessageType

@dataclass
class Transcripts:
    text: str
    json: List[dict]

def add_printing_handlers(api, transcripts, enable_partials=False,
                          speaker_change_token=False):
    """
    Adds a set of handlers to the websocket client which print out transcripts as they
    are received. This includes partials if they are enabled.

    Args:
        api (smwebsocket.client.WebsocketClient): Client instance.
        transcripts (Transcripts): Allows the transcripts to be concatenated to produce
            a final result.
        enable_partials (bool, optional): Whether or not partials are enabled.
        speaker_change_token (bool, optional): Whether to explicitly include a speaker change
            token '<sc>' in the output to indicate speaker changes.
    """
    def partial_transcript_handler(message):
        # "\n" does not appear in partial transcripts
        print(f'{message["metadata"]["transcript"]}', end='\r', file=sys.stderr)

    def transcript_handler(message):
        transcripts.json.append(message)
        transcript = message["metadata"]["transcript"]
        if transcript:
            transcript_to_print = transcript
            if speaker_change_token:
                transcript_with_sc_token = transcript.replace("\n", "\n<sc>\n")
                transcript_to_print = transcript_with_sc_token
            transcripts.text += transcript_to_print
            print(transcript_to_print)

        n_best_results = message.get("n_best_results", [])
        if n_best_results:
            n_best_list = n_best_results[0]["n_best_list"]
            for alternative in n_best_list:
                words_joined = ' '.join((word["content"] for word in alternative["words"]))
                print("* [{:.4f}] {}".format(alternative["confidence"], words_joined))
            print()

    def end_of_transcript_handler(_):
        if enable_partials:
            print("\n", file=sys.stderr)

    api.add_event_handler(ServerMessageType.AddPartialTranscript, partial_transcript_handler)
    api.add_event_handler(ServerMessageType.AddTranscript, transcript_handler)
    api.add_event_handler(ServerMessageType.EndOfTranscript, end_of_transcript_handler)


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
        play(audio)
        # seg = np.array(audio.get_array_of_samples())        
        # fig1 = plt.plot(seg)
        # plt.savefig("output/fig1.png")
        # plt.clf()


    def record_voice(self, duration, fs=16000):
        print("Recording voice...")
        # record voice for specified duration
        self.lcd_display("Speak into mic.\n Duration: %is" % duration)
        time.sleep(0.5)
        myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype="float32")
        for dur in range(duration-1, 0, -1):
            self.lcd_display("Speak into mic.\nTime left: %is" % dur, clear=False)
        sd.wait()

        # save file with timestamp
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H.%M.%S")
        rec_path = "output/recording_%s.wav" % date_time
        print("Saving recording %s..." % rec_path)
        librosa.output.write_wav(rec_path, myrecording, fs)

        return rec_path

    def predict_text_gpt2(self, gpt2_url, uni_asr_url, recording_path):
        self.lcd_display("Predicting text...\n using GPT2!")
        print(gpt2_url, uni_asr_url, recording_path)

        api = client.WebsocketClient(
        smwebsocket.models.ConnectionSettings(
            url=uni_asr_url,
            ssl_context=None))

        transcripts = Transcripts(text="", json=[])
        add_printing_handlers(api, transcripts, enable_partials=True)
        stream = sys.stdin.buffer
        # use a file for testing
        stream = open(recording_path, "rb")
        thing_to_await = api.run(
            stream,
            smwebsocket.models.TranscriptionConfig(language='en'),
            smwebsocket.models.AudioSettings()
        )
        asyncio.run(asyncio.wait_for(thing_to_await, timeout=20))

        # if this line fails you need to setup gpt-2
        response = requests.post(
            gpt2_url,
            data=transcripts.text,
            timeout=60)

        return response.text

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
        # remove high pitch problem
        cloned_voice[np.where(np.abs(cloned_voice) > cloned_voice.mean()+cloned_voice.std()*2)] = 0
        # save cloned voice
        output_path = recording_path.replace("recording", "output")
        librosa.output.write_wav(output_path, cloned_voice, output_fs)

        return output_path
    
    def reset(self):
        # clear lcd and turn off back light
        self.lcd.clear()
        self.lcd.color = [0, 0, 0]
