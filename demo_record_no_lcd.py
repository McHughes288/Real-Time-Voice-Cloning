import argparse
from pathlib import Path

import librosa
import numpy as np
from inference.encoder import inference as encoder
from inference.synthesizer.inference import Synthesizer
from inference.utils.argutils import print_args
from inference.vocoder import inference as vocoder

if __name__ == "__main__":
    ## Info & args
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-e",
        "--enc_model_fpath",
        type=Path,
        default="inference/encoder/saved_models/pretrained.pt",
        help="Path to a saved encoder",
    )
    parser.add_argument(
        "-s",
        "--syn_model_dir",
        type=Path,
        default="inference/synthesizer/saved_models/logs-pretrained/",
        help="Directory containing the synthesizer model",
    )
    parser.add_argument(
        "-v",
        "--voc_model_fpath",
        type=Path,
        default="inference/vocoder/saved_models/pretrained/pretrained.pt",
        help="Path to a saved vocoder",
    )
    parser.add_argument(
        "--low_mem",
        action="store_true",
        help="If True, the memory used by the synthesizer will be freed after each use. Adds large "
        "overhead but allows to save some GPU memory for lower-end GPUs.",
    )
    parser.add_argument(
        "--no_sound", action="store_true", help="If True, audio won't be played."
    )
    args = parser.parse_args()
    print_args(args, parser)
    if not args.no_sound:
        import sounddevice as sd

    ## Load the models one by one.
    print("Preparing the encoder, the synthesizer and the vocoder...")

    encoder.load_model(args.enc_model_fpath)
    synthesizer = Synthesizer(
        args.syn_model_dir.joinpath("taco_pretrained"),
        low_mem=args.low_mem,
        verbose=False,
    )
    vocoder.load_model(args.voc_model_fpath)

    num_generated = 0
    # fs=44100
    # rec_duration = 10  # seconds

    # myrecording = sd.rec(rec_duration * fs, samplerate=fs, channels=1, dtype='float64')
    # print("Recording Audio")
    # sd.wait()

    # sd.play(myrecording, fs)
    # sd.wait()

    # rec_path = "output/demo_record_%02d.wav" % num_generated
    # wavio.write(rec_path, myrecording, fs)

    in_fpath = "demo/johns_voice3.wav"

    ## Computing the embedding
    preprocessed_wav = encoder.preprocess_wav(in_fpath)
    print("Loaded file succesfully")

    # Then we derive the embedding.
    embed = encoder.embed_utterance(preprocessed_wav)
    print("Created the embedding")

    ## Generating the spectrogram
    text = "Hello, this is a synthesized version of John's voice, I hope that it is very impressive."

    # The synthesizer works in batch, so you need to put your data in a list or numpy array
    specs = synthesizer.synthesize_spectrograms([text], [embed])
    spec = specs[0]
    print("Created the mel spectrogram")

    ## Generating the waveform
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
    print(generated_wav.shape)
    print(synthesizer.sample_rate)
    librosa.output.write_wav(
        fpath, generated_wav.astype(np.float32), synthesizer.sample_rate
    )
    num_generated += 1
    print("\nSaved output as %s\n\n" % fpath)
