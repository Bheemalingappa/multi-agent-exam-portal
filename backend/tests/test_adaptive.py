import unittest
from app.agents.adaptive import AdaptiveChallengeEngine

class TestAdaptiveEngine(unittest.TestCase):

    def test_expert_tier_assignment(self):
        res = AdaptiveChallengeEngine.evaluate_adaptive_recommendation(95.0, 100.0, 15.0)
        self.assertEqual(res["challenge_tier"], "EXPERT")
        self.assertIn("DISTRIBUTED_FAULT_TOLERANCE", res["recommended_challenge"]["type"])

    def test_remedial_tier_assignment(self):
        res = AdaptiveChallengeEngine.evaluate_adaptive_recommendation(40.0, 30.0, 150.0)
        self.assertEqual(res["challenge_tier"], "REMEDIAL")

if __name__ == "__main__":
    unittest.main()
