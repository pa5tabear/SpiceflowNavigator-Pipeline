import asyncio
from agent_client import IngestAgentClient, StrategyAgentClient
from orchestrator import PipelineOrchestrator


def main() -> None:
    ingest = IngestAgentClient("http://localhost:8001")
    strategy = StrategyAgentClient("http://localhost:8002")
    orchestrator = PipelineOrchestrator(ingest, strategy)
    asyncio.run(orchestrator.run("https://example.com/feed"))


if __name__ == "__main__":
    main()
