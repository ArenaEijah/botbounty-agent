    def test_feasibility_accepts_supported_task(self):
        result, reasons = feasibility_check({"title": "Python API automation script", "reward_usd": 20})
        self.assertEqual(result, "FEASIBLE")
        self.assertIn("matches current technical capabilities", reasons)

    def test_feasibility_reviews_complex_task(self):
        result, reasons = feasibility_check({"title": "Complex full-stack architecture", "reward_usd": 100})
        self.assertEqual(result, "REVIEW")

    def test_feasibility_rejects_wallet_task(self):
        result, reasons = feasibility_check({"title": "Connect wallet and use private key", "reward_usd": 100})
        self.assertEqual(result, "NOT_RECOMMENDED")


if __name__ == "__main__":
    import unittest
    unittest.main()
