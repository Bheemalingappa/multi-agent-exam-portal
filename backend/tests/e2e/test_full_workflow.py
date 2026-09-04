import unittest
import uuid
from app.agents.fallback import DeterministicFallbackProvider
from app.agents.security import SecurityAgent
from app.agents.consensus import A2AConsensusEngine
from app.plagiarism.detector import PlagiarismDetector
from app.plagiarism.normalize import CodeNormalizer
from app.features.flags import FeatureFlagService
from app.billing.metering import BillingMeteringService
from app.webhooks.delivery import WebhookDeliveryService

class TestFullEndToEndWorkflow(unittest.TestCase):

    def test_complete_platform_lifecycle(self):
        # 1. Feature Flags & Billing Quota check
        self.assertTrue(FeatureFlagService.is_enabled("AI_EVALUATION"))
        self.assertTrue(BillingMeteringService.check_quota("ENTERPRISE", 500))

        # 2. Candidate source code submission
        code_pass = "def solve():\n    return 42\nprint(solve())"
        metrics = {"exit_code": 0, "execution_latency_ms": 12.5, "peak_memory_mb": 3.2}

        # 3. Static Security Scan & Security Agent
        sec_res = SecurityAgent.evaluate_security(code_pass, "E2E Test", metrics)
        self.assertEqual(sec_res["risk_level"], "LOW")
        self.assertGreaterEqual(sec_res["score"], 80.0)

        # 4. Multi-Agent Evaluation (Mentor, QA, Security)
        provider = DeterministicFallbackProvider()
        m_eval = provider.evaluate("MENTOR", code_pass, "E2E Task", metrics)
        q_eval = provider.evaluate("QA", code_pass, "E2E Task", metrics)

        # 5. A2A Consensus Negotiation
        consensus = A2AConsensusEngine.negotiate_consensus([m_eval, q_eval, sec_res])
        self.assertEqual(consensus["consensus_score"], 100.0)

        # 6. Plagiarism Similarity Check
        plag_res = PlagiarismDetector.evaluate_similarity(code_pass, "def solve(): return 42")
        self.assertIn(plag_res["plagiarism_risk_level"], ["LOW", "MEDIUM", "HIGH"])

        # 7. Signed Webhook Event Dispatch
        webhook_ok = WebhookDeliveryService.deliver_event(
            target_url="https://webhook.site/test",
            secret="whsec_test123",
            event_type="EvaluationCompleted",
            data={"score": consensus["consensus_score"]}
        )
        self.assertTrue(webhook_ok)

if __name__ == "__main__":
    unittest.main()
