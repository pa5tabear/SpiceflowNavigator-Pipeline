import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from workflow import WorkflowManager

class DummyParser:
    def __init__(self, urls):
        self.urls = urls

    def extract_audio_urls(self, xml_content: str):
        return self.urls

class DummyClient:
    def __init__(self):
        self.calls = []

    def run(self, file_path, model, task, temperature, stream):
        self.calls.append(file_path)
        return "dummy transcript"

class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        pass

def test_workflow_creates_markdown_files(tmp_path, monkeypatch):
    xml_path = Path(__file__).resolve().parent / "fixtures" / "shift_key_rss.xml"
    xml_content = xml_path.read_text()

    rss_parser = DummyParser(["http://example.com/1.mp3", "http://example.com/2.mp3"])
    runpod_client = DummyClient()

    monkeypatch.setattr("spiceflow.workflow.RSSParser", lambda: rss_parser)
    monkeypatch.setattr("spiceflow.workflow.RunPodClient", lambda: runpod_client)
    monkeypatch.setattr("spiceflow.workflow.requests.get", lambda url: DummyResponse(xml_content))

    transcripts_dir = tmp_path / "transcripts"
    manager = WorkflowManager("http://feed", transcripts_dir=transcripts_dir)
    manager.run()

    files = sorted(transcripts_dir.glob("*.md"))
    assert len(files) == 2
    assert all("dummy transcript" in f.read_text() for f in files)
