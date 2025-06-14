import asyncio
from orchestrator import PipelineOrchestrator, EventBus


class DummyIngest:
    def __init__(self):
        self.calls = []

    def discover(self, feed_url: str):
        self.calls.append(("discover", feed_url))
        return ["a.mp3", "b.mp3"]

    def transcribe(self, url: str):
        self.calls.append(("transcribe", url))
        return f"text-{url}"


class DummyStrategy:
    def __init__(self):
        self.calls = []

    def analyze(self, text: str):
        self.calls.append(("analyze", text))
        return f"summary-{text}"


class FailingIngest(DummyIngest):
    def __init__(self):
        super().__init__()
        self.fail = True

    def transcribe(self, url: str):
        if self.fail:
            self.fail = False
            self.calls.append(("transcribe", url))
            raise Exception("boom")
        return super().transcribe(url)


def test_orchestrator_sequential():
    ingest = DummyIngest()
    strategy = DummyStrategy()
    orchestrator = PipelineOrchestrator(ingest, strategy)
    result = asyncio.run(orchestrator.run("http://feed", limit=2))
    assert len(result) == 2
    assert result[0]["summary"] == "summary-text-a.mp3"


def test_orchestrator_retry():
    ingest = FailingIngest()
    strategy = DummyStrategy()
    orchestrator = PipelineOrchestrator(ingest, strategy, retries=1)
    result = asyncio.run(orchestrator.run("http://feed", limit=1))
    assert len(result) == 1
    assert ingest.calls.count(("transcribe", "a.mp3")) == 2


def test_event_bus():
    ingest = DummyIngest()
    strategy = DummyStrategy()
    bus = EventBus()
    events: list[str] = []
    bus.on("discovered", lambda urls: events.append("discovered"))
    bus.on("transcribed", lambda url, text: events.append("transcribed"))
    bus.on("analyzed", lambda url, summary: events.append("analyzed"))
    bus.on("completed", lambda results: events.append("completed"))
    orch = PipelineOrchestrator(ingest, strategy, bus=bus)
    asyncio.run(orch.run("http://feed", limit=1))
    assert events[0] == "discovered"
    assert events[-1] == "completed"

