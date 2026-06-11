# Lifeboat Runbook

The system is built and verified. These are the steps only a human (Austin)
can do, in order. Steps 0–2 take ~20 minutes total; after them the machine
runs itself.

## 0. Push the repo (one-time, ~2 min) — REQUIRED FIRST

The repo `AustinRyan/lifeboat` already exists on GitHub but the push was
rejected because the stored token lacks `workflow` scope. Run:

```bash
gh auth refresh -h github.com -s workflow   # interactive device-code login
cd ~/Projects/lifeboat && git push -u origin main
```

Then confirm the watcher runs: GitHub → repo → Actions → "Lifeboat watcher" →
**Run workflow**. From then on it runs every 30 minutes and opens a
`shutdown-alert` issue per detection. (GitHub pauses cron workflows after 60
days without repo activity — the watcher's own state commits prevent that.)

## 1. Buy the domain (~$10/yr)

Any registrar (Cloudflare Registrar is at-cost). Name ideas to check:
`lifeboat.directory`, `softwarelifeboat.com`, `sunkware.com` — anything short
that reads as "rescue". Nothing else depends on the exact name.

## 2. Deploy the site on Cloudflare Pages (free, ~10 min)

1. Cloudflare dashboard → Workers & Pages → Create → Pages → connect the
   `lifeboat` GitHub repo.
2. Settings: root directory `site`, build command `npm run build`,
   output directory `dist`.
3. Environment variable: `SITE_URL=https://<your-domain>` (also update the
   fallback in `site/astro.config.mjs`).
4. Attach the custom domain.

Every push (including the watcher's automated signal commits) now redeploys
the site.

## 3. Google Search Console (~10 min, do at launch + per guide)

Add the domain property, verify via the DNS record Cloudflare hosts, submit
`https://<domain>/rss.xml` as a feed/sitemap, and use **URL Inspection →
Request Indexing** on each new guide. This is the single highest-leverage
action per event — it pulls indexing from days down to hours.

## 4. Affiliate programs (do as guides demand)

Current guides use keys `affinity`, `canva`, `adobe`:

- **Canva** — canva.com/affiliates
- **Affinity (Serif)** — affinity.serif.com/affiliates (runs on impact.com)
- **Adobe** — adobe.com/affiliates

When approved, put the tracked URL in `site/src/data/affiliates.json`:

```json
{ "canva": "https://your-tracked-link", "affinity": "https://..." }
```

Commit; links flip from direct to tracked (with the on-page disclosure)
automatically. For future events, check each alternative vendor's site footer
for "Affiliates" or "Partners", plus partnerstack.com and impact.com
marketplaces.

## 5. Per-event playbook (the wartime drill, ~2–4 h per event)

1. A `shutdown-alert` issue arrives. Apply the go/no-go checklist in the issue.
2. **GO** → `python3 kit/new_event.py alerts/<slug>.json`
3. Research with primary sources only; replace every TODO. If the dying tool
   has a structured export, write a real migration script in a public repo and
   link it — that's the moat.
4. Commit + push → site auto-deploys.
5. Request indexing (step 3 above).
6. Reply, genuinely helpfully, in the announcement's HN/Reddit threads with
   the guide link — from your own accounts, your judgment on tone.
7. Close the issue.

## 6. Optional upgrades

- **Email alerts**: add SMTP creds as repo secrets and a `mail` step in
  `watch.yml` (GitHub notifications on new issues may already be enough —
  watch the repo and enable mobile/push notifications).
- **Reddit as a source**: requires a Reddit OAuth app (script type) —
  unauthenticated JSON is blocked. Worth it; r/selfhosted catches shutdowns
  early.
- **Backfill guides**: the signals feed already lists detected events
  (Supermaven, Fauna, Humanloop…) that can become "sunk" guides for SEO depth.
