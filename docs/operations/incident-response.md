# Incident Response Runbook

## 1. High Priority Incident Types
1. **Container Sandbox Timeout Spike**:
   - Symptoms: Multiple `TIMEOUT` execution statuses on submissions.
   - Action: Inspect Celery worker logs (`docker compose logs celery_worker`). Verify CPU bounds and Docker socket health.
2. **Database Connection Pool Exhaustion**:
   - Symptoms: FastAPI returning 500 error `QueuePool limit of size 5 overflow 10 reached`.
   - Action: Adjust `pool_size` and `max_overflow` settings in `backend/app/database/session.py`.
3. **Redis Pub/Sub Connection Failures**:
   - Symptoms: WebSockets failing to broadcast stage changes.
   - Action: Check Redis memory status via `redis-cli info memory` and restart `exam_portal_redis`.
