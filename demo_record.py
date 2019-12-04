from encoder.params_model import model_embedding_size as speaker_embedding_size
from utils.argutils import print_args
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import librosa
import argparse
import torch
import sys

import time
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd


def lcd_message(message, lcd, scroll=True):
    lcd.clear()
    lcd.blink = True
    lcd.message = message
    if scroll:
        for i in range(len(message)):
            time.sleep(0.2)
            lcd.move_left()
        lcd.clear()
        lcd.message = message
    

if __name__ == '__main__':
    ## Info & args
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-e", "--enc_model_fpath", type=Path, 
                        default="encoder/saved_models/pretrained.pt",
                        help="Path to a saved encoder")
    parser.add_argument("-s", "--syn_model_dir", type=Path, 
                        default="synthesizer/saved_models/logs-pretrained/",
                        help="Directory containing the synthesizer model")
    parser.add_argument("-v", "--voc_model_fpath", type=Path, 
                        default="vocoder/saved_models/pretrained/pretrained.pt",
                        help="Path to a saved vocoder")
    parser.add_argument("--no_sound", action="store_true", help=\
        "If True, audio won't be played.")
    args = parser.parse_args()
    print_args(args, parser)
    if not args.no_sound:
        import sounddevice as sd

    
    lcd_columns = 16
    lcd_rows = 2
    # Initialise I2C bus.
    i2c = busio.I2C(board.SCL, board.SDA)
    # Initialise the LCD class
    lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
    
    lcd.clear()
    # Set LCD color to blue
    lcd.color = [0, 100, 0]
    lcd.message = "Hackamatics 2019\nVoice Cloning"
    time.sleep(1)

    ## Load the models one by one.
    print("Preparing the encoder, the synthesizer and the vocoder...")
    lcd.clear()
    lcd.message = "Preparing models... \n"
    encoder.load_model(args.enc_model_fpath)
    synthesizer = Synthesizer(args.syn_model_dir.joinpath("taco_pretrained"), low_mem=args.low_mem)
    vocoder.load_model(args.voc_model_fpath)
    
    print("Interactive generation loop")
    num_generated = 0
    fs=44100
    rec_duration = 10  # seconds
    while True:
        try:
            

            # Get the reference audio filepath
            lcd.clear()
            lcd.message = "Speak into the microphone\n Time left: %is" % rec_duration  # seconds

            
            myrecording = sd.rec(rec_duration * fs, samplerate=fs, channels=1, dtype='float64')
            print("Recording Audio")
            time.sleep(1)
            for dur in range(rec_duration-1,0,-1):
                lcd.message = "Speak into the microphone\n Time left: %is" % dur  # seconds
                time.sleep(1)
            sd.wait()
            
            ## Computing the embedding
            preprocessed_wav = encoder.preprocess_wav(myrecording, fs)
            lcd.clear()
            lcd.message = "Loaded file succesfully \n"
            print("Loaded file succesfully")
            
            # Then we derive the embedding.
            embed = encoder.embed_utterance(preprocessed_wav)
            print("Created the embedding")
            
            
            ## Generating the spectrogram
            text = "Hello, this is a synthesized version of John's voice"
            lcd_message("Using sample sentence: %s..." % text, lcd)
            
            # The synthesizer works in batch, so you need to put your data in a list or numpy array
            specs = synthesizer.synthesize_spectrograms([text], [embed])
            spec = specs[0]
            print("Created the mel spectrogram")
            
            
            ## Generating the waveform
            lcd.clear()
            lcd.message = "Synthesizing the waveform \n"
            print("Synthesizing the waveform")
            generated_wav = vocoder.infer_waveform(spec)
            
            
            ## Post-generation
            generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")
            
            # Play the audio (non-blocking)
            if not args.no_sound:
                sd.stop()
                sd.play(generated_wav, synthesizer.sample_rate)
                
            # Save it on the disk
            fpath = "output/demo_output_%02d.wav" % num_generated
            print(generated_wav.dtype)
            librosa.output.write_wav(fpath, generated_wav.astype(np.float32), 
                                     synthesizer.sample_rate)
            num_generated += 1
            lcd.clear()
            lcd.message = "Saved output as \n %s" % fpath
            print("\nSaved output as %s\n\n" % fpath)

            time.sleep(1)
            lcd.color = [0, 0, 0]
            lcd.clear()
            time.sleep(1)
            
            
        except Exception as e:
            print("Caught exception: %s" % repr(e))
            print("Restarting\n")
        