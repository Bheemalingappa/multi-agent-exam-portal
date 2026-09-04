import unittest

try:
    from app.pipeline.tasks import MCPContextInjector, BehavioralAnomalyOracle, A2ARubricNegotiator
    from app.database.models import Exam
    HAS_EVAL = True
except ImportError:
    HAS_EVAL = False

class TestEvaluationPipeline(unittest.TestCase):

    def setUp(self):
        if HAS_EVAL:
            self.mock_exam = Exam(
                id="123e4567-e89b-12d3-a456-426614174000",
                title="Algorithm Test Task",
                description="Implement simple logic.",
                difficulty="intermediate"
            )

    @unittest.skipUnless(HAS_EVAL, "Celery/SQLAlchemy dependencies not installed in local environment")
    def test_mcp_path_traversal_protection(self):
        with self.assertRaises(ValueError):
            MCPContextInjector.sanitize_path("../../etc/passwd")

    @unittest.skipUnless(HAS_EVAL, "Celery/SQLAlchemy dependencies not installed in local environment")
    def test_mcp_context_generation_and_hashing(self):
        code = "def add(a, b):\n    return a + b"
        ctx, ctx_hash = MCPContextInjector.get_context(self.mock_exam, code)
        self.assertIn("protocol_version", ctx)
        self.assertEqual(len(ctx_hash), 64)

    @unittest.skipUnless(HAS_EVAL, "Celery/SQLAlchemy dependencies not installed in local environment")
    def test_behavioral_anomaly_oracle(self):
        telemetry = {"paste_events_count": 5, "focus_lost_count": 6, "typing_speed_wpm": 200.0}
        code = "print('hello')"
        res = BehavioralAnomalyOracle.analyze(telemetry, code)
        self.assertGreaterEqual(res["anomaly_score"], 0.70)
        self.assertTrue(len(res["signals"]) >= 2)

    @unittest.skipUnless(HAS_EVAL, "Celery/SQLAlchemy dependencies not installed in local environment")
    def test_a2a_consensus_and_explain_then_grade_report(self):
        sandbox_res = {
            "exit_code": 0,
            "stdout": "30",
            "stderr": "",
            "execution_latency_ms": 12.5,
            "peak_memory_mb": 4.2,
            "security_violation": False,
            "timed_out": False
        }
        mcp_ctx = {}
        anomaly_res = {"anomaly_score": 0.10}
        code = "def add(a, b):\n    return a + b\n\nprint(add(10, 20))"

        pkg = A2ARubricNegotiator.evaluate_and_build_report(
            sandbox_res=sandbox_res,
            mcp_context=mcp_ctx,
            anomaly_res=anomaly_res,
            submitted_code=code,
            exam=self.mock_exam
        )

        self.assertIn("Explain-Then-Grade", pkg["evaluation_report"])
        self.assertIn("1. Solution Understanding", pkg["evaluation_report"])
        self.assertIn("13. Final Grade", pkg["evaluation_report"])
        self.assertGreaterEqual(pkg["final_score"], 80.0)

if __name__ == "__main__":
    unittest.main()
