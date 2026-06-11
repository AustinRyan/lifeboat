import json
import tempfile
import unittest
from pathlib import Path

from lifeboat_watcher.events import Event, slug_for
from lifeboat_watcher.dedup import load_seen, save_seen, filter_new


def make_event(**overrides):
    fields = dict(
        source="hn",
        id="12345",
        title="Acme is shutting down",
        url="https://news.ycombinator.com/item?id=12345",
        body="",
        engagement=10,
        created_utc=1760000000,
    )
    fields.update(overrides)
    return Event(**fields)


class TestEvent(unittest.TestCase):
    def test_title_whitespace_normalized(self):
        e = make_event(title="  Acme   is\nshutting   down ")
        self.assertEqual(e.title, "Acme is shutting down")

    def test_slug_is_source_and_id(self):
        self.assertEqual(slug_for(make_event()), "hn:12345")


class TestDedup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "seen.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_missing_file_returns_empty(self):
        self.assertEqual(load_seen(self.path), set())

    def test_round_trip(self):
        save_seen(self.path, {"hn:1", "reddit:abc"})
        self.assertEqual(load_seen(self.path), {"hn:1", "reddit:abc"})
        # file is valid, sorted JSON for clean git diffs
        data = json.loads(self.path.read_text())
        self.assertEqual(data, sorted(data))

    def test_corrupt_file_returns_empty_not_crash(self):
        self.path.write_text("{not json!!")
        self.assertEqual(load_seen(self.path), set())

    def test_filter_new_returns_only_unseen(self):
        seen = {"hn:1"}
        events = [make_event(id="1"), make_event(id="2")]
        new = filter_new(events, seen)
        self.assertEqual([e.id for e in new], ["2"])


if __name__ == "__main__":
    unittest.main()
