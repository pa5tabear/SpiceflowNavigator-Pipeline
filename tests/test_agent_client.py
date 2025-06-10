import json
from agent_client import IngestAgentClient, StrategyAgentClient


class DummyResponse:
    def __init__(self, text: str):
        self.text = text
        self.status_code = 200

    def raise_for_status(self) -> None:
        pass


def test_ingest_client(monkeypatch):
    calls = {}

    def fake_post(url, *args, **kwargs):
        json_payload = kwargs.get("json")
        if url.endswith("/discover"):
            calls["discover"] = json_payload
            return DummyResponse(json.dumps({"audio_urls": ["a.mp3"]}))
        if url.endswith("/transcribe"):
            calls["transcribe"] = json_payload
            return DummyResponse("ok")
        raise AssertionError("Unexpected URL")

    monkeypatch.setattr("agent_client.requests.post", fake_post)

    client = IngestAgentClient("http://ingest")
    urls = client.discover("http://feed")
    assert urls == ["a.mp3"]
    result = client.transcribe("a.mp3")
    assert result == "ok"
    assert calls["discover"] == {"feed_url": "http://feed"}
    assert calls["transcribe"] == {"audio_url": "a.mp3"}


def test_strategy_client(monkeypatch):
    def fake_post(url, *args, **kwargs):
        if url.endswith("/analyze"):
            return DummyResponse("summary")
        if url.endswith("/score"):
            return DummyResponse(json.dumps({"score": 5}))
        raise AssertionError

    monkeypatch.setattr("agent_client.requests.post", fake_post)

    client = StrategyAgentClient("http://strategy")
    assert client.analyze("hi") == "summary"
    assert client.score("hi") == 5
