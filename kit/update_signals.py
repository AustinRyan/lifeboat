#!/usr/bin/env python3
"""Merge alerts/*.json into site/src/data/signals.json (the public feed).

Keeps the newest MAX_SIGNALS by detection recency, deduped by slug.
Run after the watcher; the Actions workflow commits the result, which
triggers a Cloudflare Pages rebuild.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ALERTS = REPO / "alerts"
OUT = REPO / "site" / "src" / "data" / "signals.json"
MAX_SIGNALS = 100


def main() -> int:
    existing = []
    if OUT.exists():
        try:
            existing = json.loads(OUT.read_text())
        except json.JSONDecodeError:
            existing = []

    by_slug = {s["slug"]: s for s in existing}
    for path in sorted(ALERTS.glob("*.json")):
        a = json.loads(path.read_text())
        by_slug[a["slug"]] = {
            "slug": a["slug"],
            "title": a["title"],
            "url": a["url"],
            "source": a["source"],
            "score": a["score"],
            "created_utc": a.get("created_utc", 0),
        }

    signals = sorted(by_slug.values(), key=lambda s: s["created_utc"], reverse=True)
    signals = signals[:MAX_SIGNALS]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(signals, indent=2) + "\n")
    print(f"wrote {len(signals)} signals to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
