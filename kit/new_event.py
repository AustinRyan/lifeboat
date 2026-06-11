#!/usr/bin/env python3
"""Strike-kit generator: scaffold a rescue-guide entry from an alert record.

Usage:
    python3 kit/new_event.py alerts/<slug>.json [--dry-run]

Creates site/src/content/events/<product-slug>.md pre-filled from the alert.
Refuses to overwrite an existing guide. The generated file contains TODO
markers that MUST be resolved (real dates, real alternatives, real export
steps) before the guide is committed — the site is a no-fake-data zone.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVENTS_DIR = REPO / "site" / "src" / "content" / "events"

TEMPLATE = """\
---
product: "{product}"
tagline: "TODO one-line description of what {product} was"
status: sinking
announced: "{announced}"
# deadline: "YYYY-MM-DD"   # TODO confirm from primary source, then uncomment
sourceUrl: "{source_url}"
# exportUrl: "https://..."  # TODO where users export their data
alternatives:
  - name: "TODO Alternative 1"
    url: "https://example.invalid"  # TODO real vendor URL
    pitch: "TODO why this is the best landing spot"
    # affiliateKey: "vendor-key"   # TODO add key to site/src/data/affiliates.json once approved
---

## What happened

TODO: 2–4 sentences. Link the announcement ({source_url}). State the deadline
and what stops working when.

## Do this before the deadline

TODO: numbered checklist — export data (exact menu path), cancel billing,
note anything that is NOT included in the export.

## Migrating your data

TODO: concrete steps per alternative. If we shipped a migration script, link
the GitHub repo and show the one-liner.
"""


def product_slug(title: str) -> str:
    """Best-effort product name from an alert title: words before the verb."""
    cut = re.split(
        r"\b(?:is|are|will|to|shuts?|shutting|sunsett?ing|winding|discontinu)\b",
        title, maxsplit=1, flags=re.IGNORECASE,
    )[0]
    slug = re.sub(r"[^a-z0-9]+", "-", cut.lower()).strip("-")
    return slug or "unnamed-product"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("alert", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    alert = json.loads(args.alert.read_text())
    title = alert["title"]
    slug = product_slug(title)
    announced = datetime.fromtimestamp(
        alert.get("created_utc") or 0, tz=timezone.utc
    ).strftime("%Y-%m-%d")

    content = TEMPLATE.format(
        product=(title.split()[0].strip(",.:;") if title else "Unknown"),
        announced=announced,
        source_url=alert["url"],
    )
    out = EVENTS_DIR / f"{slug}.md"

    if args.dry_run:
        print(f"would write: {out}")
        print(content)
        return 0
    if out.exists():
        print(f"refusing to overwrite existing guide: {out}", file=sys.stderr)
        return 1
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print(f"created {out}\nNow research the event and replace every TODO before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
