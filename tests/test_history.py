import tempfile
import unittest
from pathlib import Path

from botbounty_agent.history import BountyHistory


class HistoryTests(unittest.TestCase):
    def test_missing_history_starts_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = BountyHistory(str(Path(tmp) / "history.json"))
            self.assertFalse(history.contains("123"))

    def test_mark_and_save_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "history.json")
            history = BountyHistory(path)
            history.mark_seen("123")
            history.mark_seen(456)
            history.save()

            reloaded = BountyHistory(path)
            self.assertTrue(reloaded.contains("123"))
            self.assertTrue(reloaded.contains(456))

    def test_none_is_not_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = BountyHistory(str(Path(tmp) / "history.json"))
            history.mark_seen(None)
            history.save()
            self.assertFalse(history.contains(None))
            self.assertEqual(history.seen, set())


if __name__ == "__main__":
    unittest.main()
