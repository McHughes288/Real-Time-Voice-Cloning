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
    #print_args(args, parser)
    if not args.no_sound:
        import sounddevice as sd

    ## Load the models one by one.
    print("Preparing the encoder, the synthesizer and the vocoder...")
    encoder.load_model(args.enc_model_fpath)
    synthesizer = Synthesizer(args.syn_model_dir.joinpath("taco_pretrained"))
    vocoder.load_model(args.voc_model_fpath)


    print("\nInteractive generation loop")
    num_generated = 0
    while True:
        try:
            # Get the reference audio filepath
            message = "Reference voice: enter an wav filepath of a voice to be cloned:\n"
            in_fpath = Path(input(message).replace("\"", "").replace("\'", ""))

            ## Computing the embedding
            preprocessed_wav = encoder.preprocess_wav(in_fpath)
            print("Loaded file succesfully")

            # Derive the embedding
            embed = encoder.embed_utterance(preprocessed_wav)
            print("Created the embedding")

            ## Generating the spectrogram
            text = input("Write a sentence (+-20 words) to be synthesized:\n")
            specs = synthesizer.synthesize_spectrograms([text], [embed])
            spec = specs[0]
            print("Created the mel spectrogram")

            ## Generating the waveform
            generated_wav = vocoder.infer_waveform(spec)
            print("Synthesized the waveform")

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
            print("\nSaved output as %s\n\n" % fpath)

        except Exception as e:
            print("Caught exception: %s" % repr(e))
            print("Restarting\n")
