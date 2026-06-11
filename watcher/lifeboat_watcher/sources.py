"""Source pollers: Hacker News (Algolia), Google News RSS, Bing News RSS.

Each fetch_* function returns a list[Event] and raises nothing on bad payloads
(returns [] instead). Network errors do raise — the orchestrator catches them
per-source so one dead source never blocks the others.
"""

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from .events import Event

USER_AGENT = "Mozilla/5.0 (compatible; lifeboat-watcher/1.0)"
TIMEOUT = 15
RETRIES = 2


def _get(url: str) -> str:
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as err:  # noqa: BLE001 — retried, then re-raised
            last_err = err
            if attempt < RETRIES:
                time.sleep(1 + attempt)
    raise last_err


def _rss_id(item: ET.Element) -> str:
    guid = item.findtext("guid") or item.findtext("link") or item.findtext("title") or ""
    return hashlib.sha1(guid.encode()).hexdigest()[:16]


def _rss_ts(item: ET.Element) -> int:
    raw = item.findtext("pubDate")
    if not raw:
        return 0
    try:
        return int(parsedate_to_datetime(raw).timestamp())
    except (ValueError, TypeError):
        return 0


# --- Hacker News -----------------------------------------------------------

def parse_hn(payload: str) -> list[Event]:
    try:
        data = json.loads(payload)
        hits = data["hits"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []
    events = []
    for hit in hits:
        try:
            object_id = str(hit["objectID"])
            events.append(Event(
                source="hn",
                id=object_id,
                title=hit.get("title") or "",
                url=hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                body=hit.get("story_text") or "",
                engagement=int(hit.get("points") or 0) + int(hit.get("num_comments") or 0),
                created_utc=int(hit.get("created_at_i") or 0),
                extra={"hn_link": f"https://news.ycombinator.com/item?id={object_id}"},
            ))
        except (KeyError, TypeError, ValueError):
            continue
    return events


def fetch_hn(query: str) -> list[Event]:
    url = ("https://hn.algolia.com/api/v1/search_by_date?"
           + urllib.parse.urlencode({"query": f'"{query}"', "tags": "story", "hitsPerPage": 30}))
    return parse_hn(_get(url))


# --- RSS (shared by Google News and Bing News) ------------------------------

def _parse_rss(payload: str, source: str) -> list[Event]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return []
    events = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        if not title or not link:
            continue
        events.append(Event(
            source=source,
            id=_rss_id(item),
            title=title,
            url=link,
            body=item.findtext("description") or "",
            engagement=0,
            created_utc=_rss_ts(item),
        ))
    return events


def parse_gnews(payload: str) -> list[Event]:
    return _parse_rss(payload, "gnews")


def fetch_gnews(query: str) -> list[Event]:
    url = ("https://news.google.com/rss/search?"
           + urllib.parse.urlencode({"q": f'"{query}"', "hl": "en-US", "gl": "US", "ceid": "US:en"}))
    return parse_gnews(_get(url))


def parse_bing(payload: str) -> list[Event]:
    return _parse_rss(payload, "bing")


def fetch_bing(query: str) -> list[Event]:
    url = ("https://www.bing.com/news/search?"
           + urllib.parse.urlencode({"q": f'"{query}"', "format": "RSS"}))
    return parse_bing(_get(url))


ALL_SOURCES = {
    "hn": fetch_hn,
    "gnews": fetch_gnews,
    "bing": fetch_bing,
}
