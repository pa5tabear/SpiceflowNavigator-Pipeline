import os
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUNPOD_ENDPOINT") or not os.environ.get("RUNPOD_API_KEY"),
    reason="RUNPOD_ENDPOINT or RUNPOD_API_KEY not set",
)
def test_transcription_job_returns_job_id():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "run_transcription_job.py"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    job_id = result.stdout.strip()
    assert isinstance(job_id, str) and job_id
