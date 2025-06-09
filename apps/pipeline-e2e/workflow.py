"""Simple workflow for fetching and transcribing feeds."""
# pragma: no cover

import requests
from pathlib import Path
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "navigator-ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "common-utils"))

from rss_parser import RSSParser
from runpod_client import RunPodClient


class WorkflowManager:
    """Automate fetching podcast transcripts into Markdown files."""

    def __init__(
        self,
        feed_url: str,
        transcripts_dir: str | Path = "transcripts",
        parser: RSSParser | None = None,
        client: RunPodClient | None = None,
    ) -> None:
        self.feed_url = feed_url
        self.transcripts_dir = Path(transcripts_dir)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.parser = parser or RSSParser()
        self.client = client or RunPodClient()

    # ------------------------------------------------------------------
    def fetch_feed(self) -> str:
        resp = requests.get(self.feed_url)
        resp.raise_for_status()
        return resp.text

    # ------------------------------------------------------------------
    def get_recent_audio_urls(self, limit: int = 10) -> list[str]:
        xml = self.fetch_feed()
        urls = self.parser.extract_audio_urls(xml)
        return urls[:limit]

    # ------------------------------------------------------------------
    def _path_for_url(self, url: str) -> Path:
        name = url.split("/")[-1]
        name = name.split("?")[0]
        stem = Path(name).stem
        return self.transcripts_dir / f"{stem}.md"

    # ------------------------------------------------------------------
    def run(self) -> None:
        for url in self.get_recent_audio_urls():
            path = self._path_for_url(url)
            if path.exists():
                continue
            transcript = self.client.transcribe(url)
            content = f"# Transcript\n\nURL: {url}\n\n{transcript}\n"
            path.write_text(content)
