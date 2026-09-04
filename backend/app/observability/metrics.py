import time
from typing import Dict, Any

class MetricsCollector:
    """
    In-memory metrics counter tracking operational health:
    HTTP request latency, Celery task latency, sandbox execution throughput,
    WebSocket connections, and test case pass rates.
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.sandbox_runs = 0
        self.sandbox_timeouts = 0
        self.sandbox_security_blocks = 0
        self.websocket_connections = 0

    def record_request(self, status_code: int):
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1

    def record_sandbox(self, timed_out: bool = False, security_violation: bool = False):
        self.sandbox_runs += 1
        if timed_out:
            self.sandbox_timeouts += 1
        if security_violation:
            self.sandbox_security_blocks += 1

    def get_summary(self) -> Dict[str, Any]:
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "sandbox_runs": self.sandbox_runs,
            "sandbox_timeouts": self.sandbox_timeouts,
            "sandbox_security_blocks": self.sandbox_security_blocks,
            "websocket_connections": self.websocket_connections
        }

metrics_collector = MetricsCollector()
