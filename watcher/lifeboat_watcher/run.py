"""Orchestrator: poll all sources, dedup, score, emit alert files.

Usage:
    python3 -m lifeboat_watcher.run --out alerts/ [--state state/seen.json] [--dry-run]

Writes one alerts/<slug>.json per new above-threshold event and a matching
alerts/<slug>.md issue body. Exit 0 even if some sources fail; exit 1 only if
state cannot be persisted.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from .dedup import filter_new, load_seen, save_seen
from .events import Event, slug_for
from .scoring import ALERT_THRESHOLD, score
from .sources import ALL_SOURCES

QUERIES = [
    "shutting down",
    "shuts down",
    "sunsetting",
    "winding down",
    "discontinuing",
    "end of life",
]


def poll_all() -> tuple[list[Event], list[str]]:
    events, errors = [], []
    for source_name, fetch in ALL_SOURCES.items():
        for query in QUERIES:
            try:
                events.extend(fetch(query))
            except Exception as err:  # noqa: BLE001 — survive any single source
                errors.append(f"{source_name}({query!r}): {err}")
    # collapse duplicates returned by overlapping queries
    unique = {}
    for e in events:
        unique.setdefault(slug_for(e), e)
    return list(unique.values()), errors


def issue_body(scored) -> str:
    e = scored.event
    hn_link = e.extra.get("hn_link", "")
    lines = [
        f"**Score {scored.total}** (threshold {ALERT_THRESHOLD}) — "
        f"language {scored.breakdown['language']}, engagement {scored.breakdown['engagement']}, "
        f"negatives {scored.breakdown['negatives']}",
        "",
        f"**Title:** {e.title}",
        f"**Source:** {e.source} — {e.url}",
    ]
    if hn_link and hn_link != e.url:
        lines.append(f"**Discussion:** {hn_link}")
    if e.body:
        lines.append(f"\n> {e.body[:500]}")
    lines += [
        "",
        "## Go/No-Go checklist",
        "- [ ] Real SaaS/product shutdown (not layoffs, game server, rumor)?",
        "- [ ] Paying users who must migrate?",
        "- [ ] Shutdown date confirmed from a primary source?",
        "- [ ] Alternatives exist (check for affiliate programs)?",
        "",
        "**If GO:** run `python3 kit/new_event.py alerts/" + slug_for(e).replace(":", "-") + ".json`",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="alerts")
    parser.add_argument("--state", default="watcher/state/seen.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="print alerts without writing state or files")
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    out_dir = Path(args.out)

    events, errors = poll_all()
    for line in errors:
        print(f"source error: {line}", file=sys.stderr)

    seen = load_seen(state_path)
    new_events = filter_new(events, seen)
    scored = [score(e) for e in new_events]
    alerts = [s for s in scored if s.total >= ALERT_THRESHOLD]

    print(f"polled={len(events)} new={len(new_events)} alerts={len(alerts)} "
          f"source_errors={len(errors)}")

    for s in alerts:
        slug = slug_for(s.event).replace(":", "-")
        record = {
            "slug": slug,
            "title": s.event.title,
            "url": s.event.url,
            "source": s.event.source,
            "score": s.total,
            "breakdown": s.breakdown,
            "created_utc": s.event.created_utc,
            "body": s.event.body[:1000],
            "extra": s.event.extra,
        }
        print(f"ALERT [{s.total}] {s.event.title} — {s.event.url}")
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            safe_slug = re.sub(r"[^A-Za-z0-9_-]", "", slug)
            (out_dir / f"{safe_slug}.json").write_text(json.dumps(record, indent=2) + "\n")
            (out_dir / f"{safe_slug}.md").write_text(issue_body(s) + "\n")

    if not args.dry_run:
        try:
            save_seen(state_path, seen | {slug_for(e) for e in new_events})
        except OSError as err:
            print(f"fatal: could not persist state: {err}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
