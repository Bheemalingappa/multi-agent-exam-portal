import unittest
from app.observability.tracing import get_correlation_id, set_correlation_id
from app.observability.metrics import metrics_collector

class TestObservability(unittest.TestCase):

    def test_correlation_id_propagation(self):
        cid = set_correlation_id("test-corr-id-123")
        self.assertEqual(get_correlation_id(), "test-corr-id-123")

    def test_metrics_collector(self):
        metrics_collector.record_request(200)
        metrics_collector.record_sandbox(timed_out=False, security_violation=False)
        summary = metrics_collector.get_summary()
        self.assertGreaterEqual(summary["request_count"], 1)
        self.assertGreaterEqual(summary["sandbox_runs"], 1)

if __name__ == "__main__":
    unittest.main()
