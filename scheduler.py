import time
import json
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dep
    yaml = None
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

def _fallback_parse(text: str) -> dict:
    items: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in ("tasks:", "tasks"):
            continue
        if stripped.startswith("-"):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[1:].strip()
            if not stripped:
                continue
        if ":" in stripped:
            key, val = stripped.split(":", 1)
            if current is None:
                current = {}
            current[key.strip()] = val.strip()
    if current:
        items.append(current)
    return {"tasks": items}


@dataclass
class Task:
    name: str
    func: Callable[[], Any]
    interval: int
    retries: int = 0


class Scheduler:
    def __init__(self, tasks: list[Task], state_file: Path):
        self.tasks = tasks
        self.state_file = state_file
        self.history = self._load()

    def _load(self) -> dict[str, list[dict]]:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {t.name: [] for t in self.tasks}

    def _save(self) -> None:
        self.state_file.write_text(json.dumps(self.history))

    @classmethod
    def from_yaml(cls, path: Path, registry: dict[str, Callable]) -> "Scheduler":
        text = Path(path).read_text()
        if yaml:
            data = yaml.safe_load(text) or {}
        else:
            data = _fallback_parse(text)
        tasks = [
            Task(t["name"], registry[t["task"]], t["interval"], t.get("retries", 0))
            for t in data.get("tasks", [])
        ]
        state = Path(data.get("state_file", "scheduler_state.json"))
        return cls(tasks, state)

    def run_pending(self) -> None:
        now = time.time()
        for t in self.tasks:
            last = self.history[t.name][-1] if self.history[t.name] else None
            next_time = (last["time"] + t.interval) if last else 0
            if now >= next_time:
                self._run(t)

    def _run(self, t: Task) -> None:
        attempt = 0
        while True:
            try:
                t.func()
                status = "success"
                break
            except Exception as e:  # pragma: no cover - failure path
                status = f"fail:{e}"
                if attempt >= t.retries:
                    break
                attempt += 1
                time.sleep(2 ** attempt)
        self.history.setdefault(t.name, []).append({"time": time.time(), "status": status})
        self._save()
