import json
import pytest
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dep
    yaml = None
from pathlib import Path

from scheduler import Scheduler, Task


def test_state_persist(tmp_path):
    calls = []

    def job():
        calls.append(1)

    state = tmp_path / "state.json"
    sched = Scheduler([Task("t", job, 0)], state)
    sched.run_pending()
    sched2 = Scheduler([Task("t", job, 0)], state)
    sched2.run_pending()
    hist = json.loads(state.read_text())["t"]
    assert len(hist) == 2


def test_retry_and_backoff(tmp_path):
    count = {"n": 0}

    def job():
        count["n"] += 1
        if count["n"] < 2:
            raise ValueError("x")

    state = tmp_path / "state.json"
    sched = Scheduler([Task("t", job, 0, retries=1)], state)
    sched.run_pending()
    hist = json.loads(state.read_text())["t"]
    assert count["n"] == 2
    assert hist[-1]["status"].startswith("success")


def test_yaml_loading(tmp_path):
    if not yaml:
        pytest.skip("yaml not available")
    def job():
        pass

    cfg = {
        "state_file": str(tmp_path / "state.json"),
        "tasks": [
            {"name": "t", "task": "job", "interval": 0}
        ],
    }
    conf = tmp_path / "config.yml"
    conf.write_text(yaml.safe_dump(cfg))
    sched = Scheduler.from_yaml(conf, {"job": job})
    sched.run_pending()
    assert Path(cfg["state_file"]).exists()
