# Lifeboat 🛟

**Survival guides for sinking software.** A 24/7 watcher detects SaaS shutdown
announcements within minutes-to-hours; each confirmed event becomes a rescue
guide — deadlines, data-export steps, working migration scripts, and the best
alternatives — published while the post-announcement search surge is still
unclaimed. Alternative vendors' affiliate programs monetize the traffic.

## How it works

```
HN Algolia ─┐
Google News ─┼─► watcher (cron, 30 min) ─► dedup ─► score ─► GitHub Issue alert
Bing News  ─┘                                                      │ (human go/no-go)
                                                                   ▼
                                              kit/new_event.py ─► rescue guide
                                                                   │
                              site/ (Astro) ◄── affiliates.json ◄──┘
                                   │
                            Cloudflare Pages
```

- `watcher/` — zero-dependency Python (stdlib only). Pollers, scoring, dedup state.
- `.github/workflows/watch.yml` — runs the watcher every 30 minutes, commits
  state, opens a `shutdown-alert` issue per detection.
- `kit/new_event.py` — scaffolds a guide from an alert. `kit/update_signals.py`
  — refreshes the public signals feed.
- `site/` — Astro static site: curated guides + automated signals feed.

Nothing publishes automatically: alerts become guides only after human review
(the go/no-go checklist in each issue). The site is a no-fake-data zone —
affiliate keys without a configured URL render as honest direct links.

## Development

```bash
# watcher tests (stdlib unittest, no deps)
cd watcher && python3 -m unittest discover -s tests -v

# run the watcher locally
cd watcher && python3 -m lifeboat_watcher.run --out ../alerts --state state/seen.json

# site
cd site && npm install && npm run dev      # http://localhost:4321
cd site && npm run build                   # production build to dist/

# scaffold a guide from an alert
python3 kit/new_event.py alerts/<slug>.json
```

## Operations

See [RUNBOOK.md](RUNBOOK.md) for launch steps and the per-event playbook.
Design spec and implementation plan live in `docs/superpowers/`.
