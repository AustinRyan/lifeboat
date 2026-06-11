import unittest

from lifeboat_watcher.events import Event
from lifeboat_watcher.scoring import score, ALERT_THRESHOLD


def ev(title, body="", engagement=0, source="hn"):
    return Event(source=source, id="x", title=title, url="https://example.com",
                 body=body, engagement=engagement, created_utc=1760000000)


class TestTruePositives(unittest.TestCase):
    """Real shutdown announcement shapes must alert."""

    CASES = [
        ev("Pocket is shutting down on July 8", engagement=300),
        ev("We are sunsetting Acme Analytics after 8 years", engagement=120),
        ev("Skiff is shutting down. Export your data", engagement=900),
        ev("Acme to discontinue its CRM product in September", engagement=80),
        ev("Important: Basecamp Classic will shut down December 31", engagement=150),
        ev("Winding down Tiny Metrics", engagement=95),
    ]

    def test_all_alert(self):
        for e in self.CASES:
            with self.subTest(title=e.title):
                self.assertGreaterEqual(score(e).total, ALERT_THRESHOLD)


class TestTrueNegatives(unittest.TestCase):
    """Noise that contains shutdown-ish words must NOT alert."""

    CASES = [
        ev("Acme lays off 200, shutting down two offices", engagement=400),
        ev("Shutting down my side project after 3 months", engagement=4),
        ev("Minecraft server EpicCraft is shutting down", engagement=50),
        ev("Ask HN: Founders, where did you end up after shutting down?", engagement=200),
        ev("How to avoid your startup shutting down", engagement=90),
        ev("Government shutdown looms as Congress stalls", engagement=600),
        ev("Why is my PC shutting down randomly?", engagement=30),
    ]

    def test_none_alert(self):
        for e in self.CASES:
            with self.subTest(title=e.title):
                self.assertLess(score(e).total, ALERT_THRESHOLD)


class TestEngagement(unittest.TestCase):
    def test_engagement_boosts_score(self):
        low = score(ev("Acme is shutting down", engagement=5))
        high = score(ev("Acme is shutting down", engagement=500))
        self.assertGreater(high.total, low.total)

    def test_breakdown_is_explainable(self):
        s = score(ev("Acme is shutting down", engagement=500))
        self.assertIn("language", s.breakdown)
        self.assertIn("engagement", s.breakdown)


if __name__ == "__main__":
    unittest.main()
