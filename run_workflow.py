import asyncio
import sys
from pathlib import Path
from agent_client import IngestAgentClient, StrategyAgentClient
from orchestrator import PipelineOrchestrator, EventBus
from scheduler import _fallback_parse
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dep
    yaml = None


def _load(path: Path) -> dict:
    text = path.read_text()
    if yaml:
        return yaml.safe_load(text) or {}
    return _fallback_parse(text)


def main(cfg_file: str = "demo.yml") -> None:
    cfg = _load(Path(cfg_file))
    ingest = IngestAgentClient(cfg.get("ingest_url", "http://localhost:8001"))
    strategy = StrategyAgentClient(cfg.get("strategy_url", "http://localhost:8002"))
    bus = EventBus()
    bus.on("discovered", lambda urls: print(f"Discovered {len(urls)} URLs"))
    bus.on("transcribed", lambda url, text: print(f"Transcribed {url}"))
    bus.on("analyzed", lambda url, summary: print(f"Analyzed {url}"))
    bus.on("completed", lambda results: print(f"Completed with {len(results)} results"))
    orchestrator = PipelineOrchestrator(ingest, strategy, bus=bus)
    asyncio.run(orchestrator.run(cfg.get("feed_url", "https://example.com/feed"), cfg.get("limit", 10)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "demo.yml")
