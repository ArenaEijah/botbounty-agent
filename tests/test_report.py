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

    def test_report_includes_eligibility(self):
        bounty = {
            "id": 1,
            "title": "Eligible task",
            "reward_usd": 10,
            "_agent_priority": 75,
            "_agent_eligibility": "ELIGIBLE",
            "_agent_eligibility_reasons": ["reward and availability checks passed"],
            "_agent_feasibility": "FEASIBLE",
            "_agent_requirements_status": "READY",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            write_scan_report([bounty], interesting=[bounty], path=str(path))
            content = path.read_text(encoding="utf-8")
            self.assertIn("Eligibility", content)
            self.assertIn("ELIGIBLE", content)
            self.assertIn("reward and availability checks passed", content)

    def test_report_includes_readiness_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "report.md")
            bounty = {
                "id": "1",
                "title": "Needs review",
                "reward_usd": 20,
                "_agent_score": 70,
                "_agent_priority": 75,
                "_agent_seen_before": False,
                "_agent_requirements_status": "REVIEW",
                "_agent_requirements_reasons": ["description is too short"],
                "_agent_feasibility": "REVIEW",
                "_agent_feasibility_reasons": ["high-complexity task needs human review"],
            }
            write_scan_report([bounty], interesting=[bounty], path=path)
            report = Path(path).read_text(encoding="utf-8")
            self.assertIn("Requirements review: description is too short", report)
            self.assertIn("Feasibility review: high-complexity task needs human review", report)

    def test_report_includes_summary_counts(self):
        bounties = [
            {"id": 1, "title": "Ready", "_agent_eligibility": "ELIGIBLE", "_agent_solution_readiness": "READY"},
            {"id": 2, "title": "Review", "_agent_eligibility": "REVIEW", "_agent_solution_readiness": "REVIEW"},
            {"id": 3, "title": "Rejected", "_agent_eligibility": "NOT_ELIGIBLE", "_agent_solution_readiness": "NOT_RECOMMENDED"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "report.md")
            write_scan_report(bounties, interesting=bounties, path=path)
            report = Path(path).read_text(encoding="utf-8")
            self.assertIn("Total bounties scanned: 3", report)
            self.assertIn("Eligibility: 1 eligible, 1 review, 1 not eligible", report)
            self.assertIn("Solution readiness: 1 ready, 1 review, 1 not recommended", report)

    def test_empty_interesting_report_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "report.md")
            write_scan_report([], interesting=[], min_priority=60, path=path)
            report = Path(path).read_text(encoding="utf-8")
            self.assertIn("No opportunities currently meet the priority threshold.", report)


if __name__ == "__main__":
    unittest.main()
