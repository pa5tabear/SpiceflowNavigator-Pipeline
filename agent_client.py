"""HTTP client interfaces for communicating with other agents."""

from __future__ import annotations

import json
from urllib.parse import urljoin

import requests


class BaseAgentClient:
    """Simple HTTP client with basic GET/POST helpers."""

    def __init__(self, base_url: str, timeout: int = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # --------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        kwargs.setdefault("timeout", self.timeout)
        if method == "GET":
            resp = requests.get(url, **kwargs)
        elif method == "POST":
            resp = requests.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        resp.raise_for_status()
        return resp

    # --------------------------------------------------------------
    def get(self, path: str, **kwargs) -> str:
        return self._request("GET", path, **kwargs).text

    # --------------------------------------------------------------
    def post(self, path: str, json_data: dict | None = None, **kwargs) -> str:
        return self._request("POST", path, json=json_data, **kwargs).text


class IngestAgentClient(BaseAgentClient):
    """Client for the ingest agent."""

    def discover(self, feed_url: str) -> list[str]:
        resp = self.post("/discover", {"feed_url": feed_url})
        try:
            data = json.loads(resp)
        except json.JSONDecodeError:
            return []
        return data.get("audio_urls", [])

    def transcribe(self, audio_url: str) -> str:
        return self.post("/transcribe", {"audio_url": audio_url})


class StrategyAgentClient(BaseAgentClient):
    """Client for the strategy agent."""

    def analyze(self, text: str) -> str:
        return self.post("/analyze", {"text": text})

    def score(self, text: str) -> int:
        resp = self.post("/score", {"text": text})
        try:
            data = json.loads(resp)
            return int(data.get("score", 0))
        except (json.JSONDecodeError, ValueError):
            return 0
