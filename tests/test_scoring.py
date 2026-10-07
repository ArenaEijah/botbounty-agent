import unittest

from botbounty_agent.scoring import _reward, rank_bounties, score_bounty


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
        self.assertGreaterEqual(score, 66)
        self.assertIn("code", reasons)
        self.assertIn("technical fit", reasons)

    def test_urgent_bounty_is_penalized(self):
        score, reasons = score_bounty(
            {"title": "Urgent research task", "reward_usd": 10},
            1,
        )
        self.assertIn("time pressure", reasons)
        self.assertLess(score, 50)

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
