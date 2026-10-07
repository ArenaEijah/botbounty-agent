import unittest

from botbounty_agent.scoring import _reward, estimated_efficiency, opportunity_priority, rank_bounties, score_bounty


class ScoringTests(unittest.TestCase):
    def test_reward_accepts_numeric_value(self):
        self.assertEqual(_reward({"reward_usd": 12.5}), 12.5)

    def test_reward_accepts_dict_value(self):
        self.assertEqual(_reward({"reward": {"usd": "25"}}), 25.0)

    def test_reward_accepts_string_with_currency(self):
        self.assertEqual(_reward({"reward": "$18.50 USD"}), 18.5)

    def test_reward_defaults_to_zero(self):
        self.assertEqual(_reward({"title": "No reward"}), 0.0)

    def test_score_prefers_technical_bounty(self):
        score, reasons = score_bounty(
            {
                "title": "Python API automation task",
                "description": "Build a script",
                "reward_usd": 20,
            },
            1,
        )
        self.assertGreaterEqual(score, 64)
        self.assertIn("automation", reasons)
        self.assertIn("technical fit", reasons)

    def test_reward_tiers_and_effort_are_applied(self):
        score, reasons = score_bounty(
            {"title": "Simple Python task", "reward_usd": 50},
            1,
        )
        self.assertIn("strong reward", reasons)
        self.assertIn("likely lower effort", reasons)
        self.assertGreaterEqual(score, 68)

    def test_high_effort_task_is_penalized(self):
        score, reasons = score_bounty(
            {"title": "Complex full-stack migration", "reward_usd": 20},
            1,
        )
        self.assertIn("likely higher effort", reasons)
        self.assertIn("good reward", reasons)

    def test_urgent_bounty_is_penalized(self):
        score, reasons = score_bounty(
            {"title": "Urgent research task", "reward_usd": 10},
            1,
        )
        self.assertIn("time pressure", reasons)
        self.assertLess(score, 50)

    def test_estimated_efficiency_rewards_low_effort(self):
        efficiency, label = estimated_efficiency({"title": "Simple Python fix", "reward_usd": 20})
        self.assertEqual(efficiency, 23.0)
        self.assertEqual(label, "low effort")

    def test_estimated_efficiency_penalizes_high_effort(self):
        efficiency, label = estimated_efficiency({"title": "Complex full-stack migration", "reward_usd": 100})
        self.assertEqual(efficiency, 65.0)
        self.assertEqual(label, "high effort")

    def test_opportunity_priority_rewards_clear_requirements(self):
        priority, reasons = opportunity_priority({
            "_agent_score": 60,
            "_agent_seen_before": True,
            "reward_usd": 20,
            "title": "Python API task",
            "description": "Build an endpoint that returns JSON output and validate the expected response format.",
            "requirements": ["Input URL", "Expected output"],
        })
        self.assertEqual(priority, 70.0)
        self.assertIn("clear title", reasons)
        self.assertIn("explicit requirements", reasons)

    def test_opportunity_priority_penalizes_vague_task(self):
        priority, reasons = opportunity_priority({
            "_agent_score": 60,
            "_agent_seen_before": True,
            "reward_usd": 20,
            "title": "Help",
            "description": "Please fix this.",
        })
        self.assertEqual(priority, 48.0)
        self.assertIn("vague description", reasons)
        self.assertIn("missing requirements", reasons)

    def test_opportunity_priority_boosts_new_and_high_value(self):
        priority, reasons = opportunity_priority(
            {"_agent_score": 60, "_agent_seen_before": False, "reward_usd": 50}
        )
        self.assertEqual(priority, 80.0)
        self.assertIn("new opportunity", reasons)
        self.assertIn("high-value opportunity", reasons)

    def test_opportunity_priority_boosts_changed(self):
        priority, reasons = opportunity_priority(
            {"_agent_score": 40, "_agent_seen_before": True, "_agent_changed": True, "reward_usd": 10}
        )
        self.assertEqual(priority, 52.0)
        self.assertIn("changed opportunity", reasons)

    def test_rank_bounties_sorts_best_first(self):
        ranked = rank_bounties(
            [
                {"id": "low", "title": "Small task", "reward_usd": 2},
                {"id": "high", "title": "Python API task", "reward_usd": 20},
            ],
            1,
        )
        self.assertEqual(ranked[0]["id"], "high")
        self.assertGreater(ranked[0]["_agent_score"], ranked[1]["_agent_score"])


if __name__ == "__main__":
    unittest.main()
