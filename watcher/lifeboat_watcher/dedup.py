"""Seen-event store: a committed JSON list of slugs, append-only in practice."""

import json
import sys
from pathlib import Path

from .events import Event, slug_for


def load_seen(path: Path) -> set[str]:
    try:
        data = json.loads(Path(path).read_text())
        return set(data) if isinstance(data, list) else set()
    except FileNotFoundError:
        return set()
    except (json.JSONDecodeError, OSError) as err:
        print(f"warning: could not read {path} ({err}); treating as empty", file=sys.stderr)
        return set()


def save_seen(path: Path, seen: set[str]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(sorted(seen), indent=0) + "\n")


def filter_new(events: list[Event], seen: set[str]) -> list[Event]:
    return [e for e in events if slug_for(e) not in seen]
