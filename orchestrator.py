import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from agent_client import IngestAgentClient, StrategyAgentClient


class EventBus:
    """Minimal synchronous event dispatcher."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., None]]] = {}

    def on(self, event: str, handler: Callable[..., None]) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, **data: Any) -> None:
        for h in self._handlers.get(event, []):
            h(**data)

async def run_task(task: Callable[[], Awaitable[None]]) -> None:
    await task()

async def run_sequential(tasks: list[Callable[[], Awaitable[None]]]) -> None:
    for task in tasks:
        await run_task(task)

async def run_parallel(tasks: list[Callable[[], Awaitable[None]]]) -> None:
    await asyncio.gather(*(run_task(t) for t in tasks))


class PipelineOrchestrator:
    """Coordinate ingest and strategy agents for end-to-end execution."""

    def __init__(
        self,
        ingest: IngestAgentClient,
        strategy: StrategyAgentClient,
        retries: int = 1,
        bus: EventBus | None = None,
    ) -> None:
        self.ingest = ingest
        self.strategy = strategy
        self.retries = retries
        self.bus = bus or EventBus()

    # ----------------------------------------------------------
    def _call_with_retry(self, func: Callable[..., Any], *args: Any) -> Optional[Any]:
        for attempt in range(self.retries + 1):
            try:
                return func(*args)
            except Exception:  # pragma: no cover - external call failure
                if attempt >= self.retries:
                    return None

    # ----------------------------------------------------------
    async def _process_url(self, url: str) -> Optional[dict[str, Any]]:
        transcript = self._call_with_retry(self.ingest.transcribe, url)
        if not transcript:
            return None
        self.bus.emit("transcribed", url=url, text=transcript)
        summary = self._call_with_retry(self.strategy.analyze, transcript)
        if summary is None:
            return None
        self.bus.emit("analyzed", url=url, summary=summary)
        return {"url": url, "summary": summary}

    # ----------------------------------------------------------
    async def run(self, feed_url: str, limit: int = 10, parallel: bool = False) -> list[dict[str, Any]]:
        urls = self._call_with_retry(self.ingest.discover, feed_url) or []
        self.bus.emit("discovered", urls=urls)
        results: list[dict[str, Any]] = []

        async def handler(url: str) -> None:
            res = await self._process_url(url)
            if res:
                results.append(res)

        tasks = [lambda u=u: handler(u) for u in urls[:limit]]
        if parallel:
            await run_parallel(tasks)
        else:
            await run_sequential(tasks)

        self.bus.emit("completed", results=results)
        return results
