from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # fallback simple parser
    yaml = None

@dataclass
class Feed:
    name: str
    url: str
    strategic_importance: int | None = None

def _simple_parse(text: str) -> list[dict]:
    lines = [l.rstrip() for l in text.splitlines() if l.strip() and not l.lstrip().startswith('#')]
    items: list[dict] = []
    current: dict | None = None
    for line in lines:
        stripped = line.strip()
        if stripped == 'feeds:' or stripped == 'feeds':
            continue
        if stripped.startswith('-'):
            if current is not None:
                items.append(current)
            current = {}
            stripped = stripped[1:].strip()
            if not stripped:
                continue
        if ':' in stripped:
            key, val = stripped.split(':', 1)
            if current is None:
                current = {}
            current[key.strip()] = val.strip()
    if current:
        items.append(current)
    return items


def load_feeds(path: str | Path) -> list[Feed]:
    text = Path(path).read_text()
    if yaml:
        data = yaml.safe_load(text) or {}
        feeds = data.get('feeds', [])
    else:
        feeds = _simple_parse(text)
    return [Feed(**f) for f in feeds]
