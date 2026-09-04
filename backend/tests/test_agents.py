import unittest
from app.agents.fallback import DeterministicFallbackProvider
from app.agents.security import SecurityAgent

class TestAgents(unittest.TestCase):

    def setUp(self):
        self.provider = DeterministicFallbackProvider()
        self.metrics = {"exit_code": 0, "execution_latency_ms": 25.0, "peak_memory_mb": 4.2}

    def test_mentor_agent_evaluation(self):
        code = "def solve():\n    return 42"
        res = self.provider.evaluate("MENTOR", code, "Python Task", self.metrics)
        self.assertEqual(res["agent_type"], "MENTOR")
        self.assertGreaterEqual(res["score"], 80.0)

    def test_qa_agent_evaluation(self):
        code = "def solve():\n    return 42"
        res = self.provider.evaluate("QA", code, "Python Task", self.metrics)
        self.assertEqual(res["agent_type"], "QA")
        self.assertEqual(res["score"], 100.0)

    def test_security_agent_evaluation(self):
        code = "def solve():\n    password = 'secret'"
        res = SecurityAgent.evaluate_security(code, "Python Task", self.metrics)
        self.assertEqual(res["agent_type"], "SECURITY")
        has_credential_alert = any("Hardcoded credentials" in f for f in res["findings"])
        self.assertTrue(has_credential_alert)
        self.assertLessEqual(res["score"], 70.0)

if __name__ == "__main__":
    unittest.main()
