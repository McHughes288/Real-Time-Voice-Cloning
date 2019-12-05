import json
import shutil
import tempfile
import unittest
from pathlib import Path

import librosa
import numpy as np
from apis.batch.controllers.batch_api import jobs_post


class file_object:
    """
    Object used to proxy for the file object used in the batch api
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def save(self, output_path):
        shutil.copyfile(self.file_path, output_path)


class TestVoiceCloning(unittest.TestCase):

    def test_batch(self):

        audio = file_object("./functests/data/johns_voice3.wav")
        text = "Hello, this is a synthesized version of John's voice, I hope that it is very impressive."
        enc_model_fpath = Path("./functests/models/encoder/saved_models/pretrained.pt")
        syn_model_dir = Path("./functests/models/synthesizer/saved_models/logs-pretrained/taco_pretrained")
        voc_model_fpath = Path("./functests/models/vocoder/saved_models/pretrained/pretrained.pt")
        
        generated_output = "./output/functest_output.wav"
        generated_compare = "./functests/data/johns_generated.wav"

        batch_json = jobs_post(
            audio,
            text,
            enc_model_fpath=enc_model_fpath,
            syn_model_dir=syn_model_dir,
            voc_model_fpath=voc_model_fpath,
            tmp_dir=tempfile.mkdtemp()
        )

        data = json.loads(batch_json)["result"]
        voice = np.array(data["generated_voice"]).astype(np.float32)
        fs = data["sample_rate"]

        librosa.output.write_wav(
            generated_output, voice, fs
        )

        output_voice, output_fs = librosa.load(generated_output)
        compare_voice, compare_fs = librosa.load(generated_compare)

        #self.assertEqual(output_voice.shape, compare_voice.shape)
        self.assertEqual(output_fs, compare_fs)
