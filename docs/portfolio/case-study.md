# Multi-Agent Exam Portal — Engineering Architecture Case Study

## 1. Problem Statement
Evaluating candidate technical submissions in modern hiring requires executing arbitrary untrusted code safely, providing instant real-time feedback, preventing cheating via plagiarism and prompt injection, and scaling worker execution without incurring unbounded cloud costs.

## 2. Engineering Trade-offs & Decisions
1. **Asynchronous Task Architecture**:
   - *Decision*: Decoupled REST ingestion from Celery task execution via Redis Pub/Sub.
   - *Trade-off*: Adds worker scaling complexity, but ensures FastAPI HTTP gateway never blocks on sandbox executions.
2. **Ephemeral Sandbox Virtualization**:
   - *Decision*: Docker SDK Alpine container (`10001:10001`, `network_mode="none"`, `read_only=True`, 128MB RAM).
   - *Trade-off*: Requires mounting Docker socket `/var/run/docker.sock` to Celery workers, mitigated by node pool isolation.
3. **Deterministic AI Fallback**:
   - *Decision*: Integrated Circuit Breaker state machine routing failures to `DeterministicFallbackProvider`.
   - *Trade-off*: Ensures 100% evaluation availability during LLM vendor outages without corrupting scores.
