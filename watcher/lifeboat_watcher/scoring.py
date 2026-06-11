"""Shutdown-language scoring with explainable breakdown.

total = language + engagement - negatives. Alert when total >= ALERT_THRESHOLD.
Language is required: an event with zero language signal never alerts no
matter how popular it is.
"""

import math
import re
from dataclasses import dataclass

from .events import Event

ALERT_THRESHOLD = 70

# Announcement-shaped phrasing: the product itself is being ended.
STRONG = re.compile(
    r"\b(?:is|are|will be)\s+shutting\s+down\b"
    r"|\bshut(?:s|ting)?\s+down\s+(?:on|in|at|this|next|december|january|february|march"
    r"|april|may|june|july|august|september|october|november)\b"
    r"|\bwill\s+shut\s+down\b"
    r"|\bsunset(?:s|ting)?\b"
    r"|\b(?:to\s+)?discontinu(?:e|es|ing|ed)\b"
    r"|\bend\s+of\s+life\b"
    r"|\bwinding\s+down\b"
    r"|\bclosing\s+(?:its|their)\s+doors\b",
    re.IGNORECASE,
)
WEAK = re.compile(r"\bshut(?:ting)?\s+down\b|\bshutdown\s+of\b", re.IGNORECASE)

# Shapes that contain shutdown words but are not a SaaS product dying.
NEGATIVE = re.compile(
    r"\blay(?:s|ing)?\s+off\b|\blaid\s+off\b|\blayoffs?\b"
    r"|\bmy\s+(?:side\s+)?project\b|\bside\s+project\b"
    r"|\bminecraft\b|\bgame\s+server\b|\bguild\b"
    r"|\bask\s+hn\b|\bshow\s+hn\b"
    r"|\bhow\s+to\b|\bwhy\s+(?:is|do|does|did)\b|\bavoid\b"
    r"|\bgovernment\s+shutdown\b|\bcongress\b|\bsenate\b"
    r"|\bmy\s+(?:pc|computer|laptop|phone|mac)\b|\brandomly\b"
    r"|\bfactory\b|\bplant\b|\bstores?\s+closing\b|\boffices\b"
    r"|\brestaurants?\b|\bnuclear\b|\breactor\b|\bpipeline\b|\bhighway\b",
    re.IGNORECASE,
)


@dataclass
class ScoredEvent:
    event: Event
    total: int
    breakdown: dict


def _language_points(event: Event) -> int:
    if STRONG.search(event.title):
        return 60
    if STRONG.search(event.body):
        return 30
    if WEAK.search(event.title):
        return 25
    if WEAK.search(event.body):
        return 10
    return 0


def _engagement_points(event: Event) -> int:
    return min(30, round(10 * math.log10(event.engagement + 1)))


def _negative_points(event: Event) -> int:
    text = f"{event.title} {event.body}"
    return 50 if NEGATIVE.search(text) else 0


def score(event: Event) -> ScoredEvent:
    language = _language_points(event)
    engagement = _engagement_points(event)
    negatives = _negative_points(event)
    total = (language + engagement - negatives) if language > 0 else 0
    return ScoredEvent(
        event=event,
        total=total,
        breakdown={"language": language, "engagement": engagement, "negatives": -negatives},
    )
