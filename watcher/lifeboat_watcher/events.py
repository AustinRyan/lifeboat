"""Common event record produced by every source poller."""

from dataclasses import dataclass, field


def _normalize(text: str) -> str:
    return " ".join(text.split())


@dataclass
class Event:
    source: str          # "hn" | "reddit" | "gnews"
    id: str              # source-native unique id
    title: str
    url: str             # canonical discussion/article URL
    body: str = ""
    engagement: int = 0  # points/score/comments — source's best popularity proxy
    created_utc: int = 0
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.title = _normalize(self.title)
        self.body = _normalize(self.body)


def slug_for(event: Event) -> str:
    return f"{event.source}:{event.id}"
