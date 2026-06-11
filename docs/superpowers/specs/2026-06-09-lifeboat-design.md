# Lifeboat — SaaS Shutdown Response Engine

**Date:** 2026-06-09
**Status:** Approved by owner (Austin), affiliate-first model selected.

## One-liner

A 24/7 watcher detects SaaS shutdown announcements within minutes-to-hours; a
strike kit turns each confirmed event into a published, genuinely useful rescue
page (facts, deadlines, best alternatives, working migration script) that
carries affiliate links — captured while the post-announcement search surge is
still unclaimed.

## Why this works

When a SaaS product announces shutdown, its paying customers must migrate on a
deadline. Search volume for "<product> shutting down" / "<product> alternative"
spikes immediately, and for the first 24–72 hours almost nothing ranks because
the news is too fresh. First-mover pages with real utility win that surge.
Alternative vendors pay affiliate commissions ($50–200/signup or 20–30%
recurring) for exactly these customers.

Revenue model: **affiliate-first**. Building per-event clone products was
considered and rejected (days of build time per event, only viable for trivial
tools). A clone remains a per-event judgment call, not part of this system.

## Components

### 1. Watcher (peacetime engine — runs forever, $0)

- Scheduled job: GitHub Actions cron, every 30 minutes.
- Sources (all free, no API keys):
  - Hacker News via Algolia search API (`search_by_date`, story tag), query
    patterns: "shutting down", "shuts down", "sunsetting", "discontinuing",
    "end of life", "winding down".
  - Reddit public JSON search across r/SaaS, r/selfhosted, r/webdev,
    r/Entrepreneur, r/smallbusiness, r/sysadmin.
  - Google News RSS for the same query patterns.
- Pipeline: poll → normalize to a common Event record → dedup against a
  committed JSON state file (`watcher/state/seen.json`) → score → alert.
- Scoring signals: shutdown-language confidence (title/body regex tiers),
  engagement (HN points/comments, Reddit score), product-ness heuristics
  (excludes layoffs-only news, game servers, rumors, hardware recalls).
- Alerting: events above threshold open a **GitHub Issue** in this repo with a
  summary, links, score breakdown, and go/no-go checklist. Optional SMTP email
  via repository secrets. **Nothing publishes automatically** — the owner
  confirms each strike. False positives die at this gate.

### 2. Strike kit (wartime — hours per confirmed event)

On a confirmed event:

- `kit/new_event.py` scaffolds a rescue page entry (content collection) from
  the event record.
- Rescue page contents: shutdown timeline and facts, "do this before <date>"
  checklist, comparison of the best 2–4 alternatives, migration guide.
- A real, open-source migration script (per event, written at strike time)
  converting the dying tool's export format to the top alternatives' import
  formats — the credibility moat over thin listicles.
- Affiliate links resolved from `site/src/data/affiliates.json`; until an
  affiliate ID exists for a vendor, pages render honest direct links (no
  fake/placeholder URLs ever shipped).
- Distribution: Google Search Console index request; helpful replies in the
  announcement's HN/Reddit threads posted by the owner under his accounts.

### 3. Directory site (the compounding asset)

- One domain, static site (Astro), deployed on Cloudflare Pages free tier.
- Permanent public directory of SaaS shutdowns + survival guides. Each event
  adds a page; old pages keep earning from stragglers and build domain
  authority so each new strike ranks faster.
- Watcher feed also populates a "recently observed shutdown signals" index
  (clearly labeled as automated detections, distinct from curated guides).

### 4. Money flow & human-only steps

Affiliate payouts go directly to the owner's accounts. Owner-only steps:
buy domain (~$10), connect repo to Cloudflare Pages, push repo to GitHub and
enable Actions, create Search Console property, sign up for affiliate programs
as events demand, approve each strike (close the GitHub Issue with go/no-go),
post outreach replies. Everything else is automated or producible by Claude.

## Error handling

- Each source poller fails independently; one source erroring never blocks the
  others. Failures are logged to the Actions run and surfaced in the issue
  body of the next successful run if persistent.
- Network calls have timeouts and bounded retries.
- Dedup state is append-only JSON committed by the Actions workflow; corrupt
  state falls back to empty-with-warning rather than crashing.

## Testing

- Unit tests per source parser using recorded fixtures (real captured API
  responses) so upstream format drift fails loudly.
- Scoring tests: known-true recent shutdown headlines must score above
  threshold; known-false (layoffs, game servers, "shutting down my side
  project" blog posts) must score below.
- Live backtest before first deploy: watcher run against real current data
  must detect at least one known real recent shutdown.

## Costs

Domain ~$10/yr. Hosting $0 (Cloudflare Pages). Monitoring $0 (GitHub Actions
free tier; public repo). No paid APIs (Twitter/X excluded by design).

## Honest expectations

Revenue per event ranges $0 (tiny tool, no affiliate programs among
alternatives) to thousands (large tool, strong programs). Several notable SaaS
shutdowns occur per month historically; first $1,000 may take weeks to months.
Cost of waiting is ~$0 and the directory compounds.
