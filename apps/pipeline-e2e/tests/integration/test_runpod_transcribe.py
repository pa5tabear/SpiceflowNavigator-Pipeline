import pytest
import os
import sys
from pathlib import Path

# Add path for RunPodClient
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs" / "common-utils"))

from runpod_client import RunPodClient
from gradio_client import utils

AUDIO_URL = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUNPOD_ENDPOINT"),
    reason="RUNPOD_ENDPOINT not set",
)
def test_runpod_transcribe_live():
    client = RunPodClient()
    audio_path = utils.handle_file(AUDIO_URL)
    result = client.run(
        file_path=audio_path,
        model="Systran/faster-whisper-large-v3",
        task="transcribe",
        temperature=0.0,
        stream=False,
    )
    assert isinstance(result, str) and result.strip()


