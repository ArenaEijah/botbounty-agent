import tempfile
import unittest
from pathlib import Path

from botbounty_agent.report import write_scan_report


class ReportTests(unittest.TestCase):
    def test_report_contains_only_interesting_opportunities(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "report.md")
            ranked = [
                {"id": "1", "title": "High", "reward_usd": 50, "_agent_score": 70, "_agent_priority": 80, "_agent_seen_before": False},
                {"id": "2", "title": "Low", "reward_usd": 2, "_agent_score": 30, "_agent_priority": 35, "_agent_seen_before": True},
            ]
            write_scan_report(ranked, interesting=[ranked[0]], min_priority=60, path=path)
            report = Path(path).read_text(encoding="utf-8")
            self.assertIn("High", report)
            self.assertNotIn("| Low |", report)
            self.assertIn("priority >= 60", report)

    def test_empty_interesting_report_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "report.md")
            write_scan_report([], interesting=[], min_priority=60, path=path)
            report = Path(path).read_text(encoding="utf-8")
            self.assertIn("No opportunities currently meet the priority threshold.", report)


if __name__ == "__main__":
    unittest.main()
