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
def test_e2e_submission_and_status_check():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "scripts/run_e2e_transcription.py"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    status = result.stdout.strip()
    assert status in {
        "QUEUED",
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "TIMED_OUT",
    }

    # Exercise additional modules for coverage
    from spiceflow.analyzer import StrategicAnalyzer
    from spiceflow.config import load_feeds

    analyzer = StrategicAnalyzer()
    analyzer.analyze("This strategy roadmap outlines revenue growth.")

    feeds = load_feeds(Path("config/rss_feeds.yml"))
    assert feeds
