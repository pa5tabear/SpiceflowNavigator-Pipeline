import os
import wave
import requests
import types
import pytest
import sys
from pathlib import Path

# Add paths for all needed modules
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs" / "common-utils"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "apps" / "navigator-ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "apps" / "navigator-strategy"))

from runpod_client import RunPodClient
from cli import main as cli_main
from analyzer import StrategicAnalyzer
from config import load_feeds
from rss_parser import RSSParser
from workflow import WorkflowManager


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUNPOD_ENDPOINT"),
    reason="RUNPOD_ENDPOINT not set",
)
def test_proxy_transcription(tmp_path, monkeypatch):
    audio_file = tmp_path / "temp.wav"
    with wave.open(str(audio_file), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)

    class DummyPredict:
        def __init__(self, endpoint):
            self.endpoint = endpoint

        def predict(self, *args, **kwargs):
            return "ok"

    monkeypatch.setattr("runpod_client.Client", DummyPredict)
    monkeypatch.setattr(
        "runpod_client.requests.get",
        lambda url, timeout=5: types.SimpleNamespace(
            raise_for_status=lambda: None, status_code=200
        ),
    )
    client = RunPodClient()
    resp = requests.get(client.endpoint, timeout=5)
    assert resp.status_code == 200
    result = client.transcribe(str(audio_file))
    assert isinstance(result, str) and result.strip()

    yaml_path = tmp_path / "feeds.yml"
    yaml_path.write_text(
        "feeds:\n  - name: Test\n    url: http://a\n    strategic_importance: 1\n"
    )
    feeds = load_feeds(yaml_path)
    assert feeds[0].name == "Test"
    analyzer = StrategicAnalyzer()
    summary = analyzer.analyze("Our growth strategy is solid.")
    assert "strategy" in summary.lower()

    class DummyClient:
        def __init__(self, endpoint=None):
            self.calls = []

        def transcribe(self, path):
            self.calls.append(path)
            return "hi"

    monkeypatch.setattr("cli.RunPodClient", DummyClient)
    cli_main(["file.wav"])

    parser = RSSParser()
    xml = "<rss><channel><item><enclosure url='a.mp3'/></item><item><enclosure url='b.mp3'/></item></channel></rss>"
    monkeypatch.setattr("workflow.RSSParser", lambda: parser)
    monkeypatch.setattr(
        "workflow.requests.get",
        lambda url: type(
            "R", (), {"text": xml, "raise_for_status": lambda self: None}
        )(),
    )
    monkeypatch.setattr("workflow.RunPodClient", lambda: DummyClient())
    manager = WorkflowManager("http://feed", transcripts_dir=tmp_path)
    manager.run()
    files = sorted(tmp_path.glob("*.md"))
    assert len(files) == 2


def test_rss_and_analysis(tmp_path):
    yaml_path = tmp_path / "feeds.yml"
    yaml_path.write_text(
        "feeds:\n  - name: Test\n    url: http://a\n    strategic_importance: 1\n"
    )
    feeds = load_feeds(yaml_path)
    assert feeds[0].name == "Test"
    analyzer = StrategicAnalyzer()
    summary = analyzer.analyze("Our growth strategy is solid.")
    assert "strategy" in summary.lower()


def test_cli_and_workflow(tmp_path, monkeypatch):
    class DummyClient:
        def __init__(self, endpoint=None):
            self.calls = []

        def transcribe(self, path):
            self.calls.append(path)
            return "hi"

    monkeypatch.setattr("cli.RunPodClient", DummyClient)
    cli_main(["file.wav"])

    parser = RSSParser()
    xml = "<rss><channel><item><enclosure url='a.mp3'/></item><item><enclosure url='b.mp3'/></item></channel></rss>"
    monkeypatch.setattr("workflow.RSSParser", lambda: parser)
    monkeypatch.setattr(
        "workflow.requests.get",
        lambda url: type(
            "R", (), {"text": xml, "raise_for_status": lambda self: None}
        )(),
    )
    monkeypatch.setattr("workflow.RunPodClient", lambda: DummyClient())
    manager = WorkflowManager("http://feed", transcripts_dir=tmp_path)
    manager.run()
    files = sorted(tmp_path.glob("*.md"))
    assert len(files) == 2
