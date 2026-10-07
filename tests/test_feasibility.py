import unittest

from botbounty_agent.scoring import feasibility_check
from botbounty_agent.main import _draft_deliverable, _execution_plan, _generate_solution_files


class FeasibilityTests(unittest.TestCase):
    def test_feasibility_accepts_supported_task(self):
        result, reasons = feasibility_check({"title": "Python API automation script", "reward_usd": 20})
        self.assertEqual(result, "FEASIBLE")
        self.assertIn("matches current technical capabilities", reasons)

    def test_feasibility_reviews_complex_task(self):
        result, reasons = feasibility_check({"title": "Complex full-stack architecture", "reward_usd": 100})
        self.assertEqual(result, "REVIEW")

    def test_execution_plan_is_read_only_and_structured(self):
        plan = _execution_plan({"title": "Python API automation fix"})
        self.assertGreaterEqual(len(plan), 5)
        self.assertTrue(any("API" in step for step in plan))
        self.assertTrue(any("do not submit" in step for step in plan))

    def test_draft_deliverable_is_safe(self):
        draft = _draft_deliverable({"title": "Python API automation"})
        self.assertIn("# Draft Deliverable", draft)
        self.assertIn("This is a draft only", draft)
        self.assertNotIn("private key", draft.lower())

    def test_solution_scaffold_generation_is_safe(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                import os
                os.chdir(tmp)
                root = _generate_solution_files("123", {"title": "Python API task", "description": "Build an API script"})
                self.assertTrue((root / "README.md").exists())
                self.assertTrue((root / "solution.py").exists())
                self.assertTrue((root / "test_solution.py").exists())
                self.assertTrue((root / "SOLUTION_SPEC.md").exists())
                self.assertIn("Acceptance checklist", (root / "SOLUTION_SPEC.md").read_text())
                self.assertIn("Draft", (root / "README.md").read_text())
            finally:
                os.chdir(original)

    def test_feasibility_rejects_wallet_task(self):
        result, reasons = feasibility_check({"title": "Connect wallet and use private key", "reward_usd": 100})
        self.assertEqual(result, "NOT_RECOMMENDED")


if __name__ == "__main__":
    unittest.main()
