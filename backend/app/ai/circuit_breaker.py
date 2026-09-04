import time
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is OPEN to trigger deterministic fallback."""
    pass

class CircuitBreaker:
    """
    Production Circuit Breaker state machine protecting LLM providers:
    CLOSED (normal) -> OPEN (after failure threshold) -> HALF_OPEN (after cooldown).
    """

    def __init__(self, failure_threshold: int = 3, recovery_cooldown_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_cooldown_seconds = recovery_cooldown_seconds
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_state_change = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_state_change > self.recovery_cooldown_seconds:
                self.state = "HALF_OPEN"
                self.last_state_change = now
                logger.info("Circuit Breaker transitioned to HALF_OPEN state.")
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        if self.state != "CLOSED":
            self.state = "CLOSED"
            self.last_state_change = time.time()
            logger.info("Circuit Breaker reset to CLOSED state.")

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            logger.warning(f"Circuit Breaker tripped to OPEN state after {self.failure_count} failures.")

global_circuit_breaker = CircuitBreaker()
