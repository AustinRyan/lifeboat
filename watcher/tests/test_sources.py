import unittest
from pathlib import Path

from lifeboat_watcher.sources import parse_hn, parse_gnews, parse_bing

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseHN(unittest.TestCase):
    def setUp(self):
        self.events = parse_hn((FIXTURES / "hn.json").read_text())

    def test_returns_events(self):
        self.assertGreater(len(self.events), 0)

    def test_fields_populated(self):
        e = self.events[0]
        self.assertEqual(e.source, "hn")
        self.assertTrue(e.id)
        self.assertTrue(e.title)
        self.assertTrue(e.url.startswith("http"))
        self.assertIsInstance(e.engagement, int)
        self.assertGreater(e.created_utc, 0)

    def test_malformed_returns_empty(self):
        self.assertEqual(parse_hn("{not json"), [])
        self.assertEqual(parse_hn('{"unexpected": 1}'), [])


class TestParseGoogleNews(unittest.TestCase):
    def setUp(self):
        self.events = parse_gnews((FIXTURES / "gnews.xml").read_text())

    def test_returns_events(self):
        self.assertGreater(len(self.events), 0)

    def test_fields_populated(self):
        e = self.events[0]
        self.assertEqual(e.source, "gnews")
        self.assertTrue(e.id)
        self.assertTrue(e.title)
        self.assertTrue(e.url.startswith("http"))
        self.assertGreater(e.created_utc, 0)

    def test_malformed_returns_empty(self):
        self.assertEqual(parse_gnews("<rss><oops"), [])
        self.assertEqual(parse_gnews("plain text"), [])


class TestParseBing(unittest.TestCase):
    def setUp(self):
        self.events = parse_bing((FIXTURES / "bingnews.xml").read_text())

    def test_returns_events(self):
        self.assertGreater(len(self.events), 0)

    def test_fields_populated(self):
        e = self.events[0]
        self.assertEqual(e.source, "bing")
        self.assertTrue(e.id)
        self.assertTrue(e.title)
        self.assertTrue(e.url.startswith("http"))

    def test_malformed_returns_empty(self):
        self.assertEqual(parse_bing("<rss><oops"), [])


class TestStableIds(unittest.TestCase):
    def test_rss_ids_stable_across_parses(self):
        xml = (FIXTURES / "gnews.xml").read_text()
        a = [e.id for e in parse_gnews(xml)]
        b = [e.id for e in parse_gnews(xml)]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
