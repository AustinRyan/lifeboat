#!/bin/zsh
# Lifeboat local watcher run: poll -> signals -> issues -> push -> deploy site.
# Scheduled by ~/Library/LaunchAgents/com.austinryan.lifeboat-watcher.plist
# (every 30 min + at load). Logs: ops/logs/watcher.log
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

REPO="$HOME/Projects/lifeboat"
LOCK="$REPO/ops/.run.lock"
cd "$REPO"

mkdir "$LOCK" 2>/dev/null || { echo "$(date -u +%FT%TZ) already running, skipping"; exit 0; }
trap 'rmdir "$LOCK"' EXIT

echo "=== $(date -u +%FT%TZ) watcher run ==="
git pull --rebase --quiet 2>/dev/null || true

( cd watcher && python3 -m lifeboat_watcher.run --out ../alerts --state state/seen.json )
python3 kit/update_signals.py

# Open a GitHub issue once per alert; alerts/.issued tracks what's been raised.
touch alerts/.issued
for f in alerts/*.md(N); do
  slug="$(basename "$f" .md)"
  grep -qx "$slug" alerts/.issued && continue
  title="$(python3 -c "import json;print(json.load(open('alerts/$slug.json'))['title'][:200])")"
  if gh issue create --repo AustinRyan/lifeboat \
       --title "🛟 $title" --body-file "$f" --label shutdown-alert >/dev/null; then
    echo "$slug" >> alerts/.issued
    echo "issue opened: $title"
  else
    echo "issue creation failed for $slug (will retry next run)"
  fi
done

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "watcher: state and signals update"
  git push --quiet && echo "pushed state"
fi

# Rebuild + publish the site when content or signals changed since last deploy.
STAMP="$REPO/ops/.last-deploy"
HEAD_NOW="$(git rev-parse HEAD)"
if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$HEAD_NOW" ]; then
  ( cd site \
    && SITE_URL="https://austinryan.github.io/lifeboat/" BASE_PATH="/lifeboat" npm run build >/dev/null 2>&1 \
    && npx gh-pages -d dist --nojekyll -m "deploy site" >/dev/null 2>&1 ) \
    && { echo "$HEAD_NOW" > "$STAMP"; echo "site deployed"; } \
    || echo "site deploy failed"
fi
echo "=== done ==="
