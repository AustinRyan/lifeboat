# Lifeboat Runbook

## Current state: fully automated, zero required maintenance

- **Watcher**: runs on this Mac every 30 minutes via launchd
  (`~/Library/LaunchAgents/com.austinryan.lifeboat-watcher.plist` →
  `ops/run_watcher.sh`). It polls sources, commits state, pushes, and opens a
  `shutdown-alert` GitHub Issue per new detection. Logs:
  `ops/logs/watcher.log`. It only runs while the Mac is awake — detections
  queue up and are caught on the next run.
- **Site**: deployed to **https://austinryan.github.io/lifeboat/** via the
  `gh-pages` branch; the watcher redeploys automatically when content changes.
- **Alerts**: watch the repo (GitHub → Watch → All activity) to get
  emails/push notifications when an issue opens.

Useful commands:

```bash
tail -f ~/Projects/lifeboat/ops/logs/watcher.log            # watch it work
launchctl kickstart gui/$UID/com.austinryan.lifeboat-watcher # force a run now
launchctl bootout gui/$UID/com.austinryan.lifeboat-watcher   # stop it
```

## The one revenue-critical step (requires your identity)

Affiliate programs need a human's name, address, and payout details — this is
the only thing standing between traffic and money. Current guides use keys
`affinity`, `canva`, `adobe`:

- **Canva** — canva.com/affiliates
- **Affinity (Serif)** — affinity.serif.com/affiliates (runs on impact.com)
- **Adobe** — adobe.com/affiliates

When approved, put each tracked URL in `site/src/data/affiliates.json`:

```json
{ "canva": "https://your-tracked-link", "affinity": "https://..." }
```

Commit + push; the next watcher run redeploys and links flip from direct to
tracked (with the on-page disclosure). Until then the site runs fine with
honest direct links — it just earns nothing.

## Per-event playbook (when a shutdown-alert issue arrives)

1. Apply the go/no-go checklist in the issue.
2. **GO** → `python3 kit/new_event.py alerts/<slug>.json`
3. Research with primary sources only; replace every TODO. If the dying tool
   has a structured export, write a real migration script in a public repo
   and link it — that's the moat.
4. Commit + push; the watcher deploys it within 30 minutes (or kickstart).
5. Reply, genuinely helpfully, in the announcement's HN/Reddit threads with
   the guide link — your accounts, your judgment on tone.
6. Close the issue.

## Optional upgrades (each helps growth, none required)

- **Custom domain (~$10/yr)**: buy one, point DNS at GitHub Pages, set it in
  repo Settings → Pages, then update `SITE_URL`/`BASE_PATH` in
  `ops/run_watcher.sh` (drop the base path) and `site/astro.config.mjs`.
- **Google Search Console**: verify the site and request indexing per guide —
  the single biggest accelerator for catching the post-announcement search
  surge (hours instead of days).
- **GitHub Actions cron instead of launchd** (runs even when the Mac is off):
  `gh auth refresh -h github.com -s workflow`, then restore
  `ops/github-actions-watch.yml.disabled` to `.github/workflows/watch.yml`
  and push.
- **Reddit as a source**: needs a Reddit OAuth app; unauthenticated JSON is
  blocked. r/selfhosted catches shutdowns early.
- **Backfill guides**: the signals feed lists detected events (Supermaven,
  Fauna, Humanloop…) that can become "sunk" guides for SEO depth.
