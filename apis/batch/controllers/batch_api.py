import json

import numpy as np
from inference.encoder import inference as encoder
from inference.synthesizer.inference import Synthesizer
from inference.vocoder import inference as vocoder


def jobs_post(
    audio,
    text,
    enc_model_fpath="/model/encoder.pt",
    syn_model_dir="/model/synthesizer/",
    voc_model_fpath="/model/vocoder.pt",
) -> str:

    print("Preparing the encoder, the synthesizer and the vocoder...")

    encoder.load_model(enc_model_fpath)
    synthesizer = Synthesizer(syn_model_dir.joinpath("taco_pretrained"), verbose=False,)
    vocoder.load_model(voc_model_fpath)

    # save file locally in container
    in_fpath = "/temp.audio"
    audio.save(in_fpath)

    ## Computing the embedding
    preprocessed_wav = encoder.preprocess_wav(in_fpath)
    print("Loaded file succesfully")

    # Then we derive the embedding.
    embed = encoder.embed_utterance(preprocessed_wav)
    print("Created the embedding")

    ## Generating the spectrogram
    specs = synthesizer.synthesize_spectrograms([text], [embed])
    spec = specs[0]
    print("Created the mel spectrogram")

    ## Generating the waveform
    print("Synthesizing the waveform")
    generated_wav = vocoder.infer_waveform(spec)

    ## Post-generation
    generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

    data = {}
    data["result"] = {
        "generated_voice": generated_wav.astype(np.float32),
        "synthesizer_sample_rate": synthesizer.sample_rate,
    }

    # librosa.output.write_wav(
    #     fpath, generated_wav.astype(np.float32), synthesizer.sample_rate
    # )

    return json.dumps(data)
