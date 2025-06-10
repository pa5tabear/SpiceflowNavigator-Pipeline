import os
import types

class Client:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def predict(self, *args, **kwargs):
        return "ok"

class RunPodClient:
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or os.environ.get("RUNPOD_ENDPOINT", "http://local")

    def transcribe(self, file_path: str) -> str:
        return "dummy transcript"

    def run(self, **kwargs) -> str:
        return "dummy transcript"

# provide a requests-like object for monkeypatching
requests = types.SimpleNamespace(get=lambda url, timeout=5: Client(url))
