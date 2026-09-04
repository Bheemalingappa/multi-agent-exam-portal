# Operational Runbook: FastAPI Gateway Service Outage

## 1. Symptoms & Impact
- High HTTP 5xx error rate on `/api/v1/` endpoints.
- Readiness probe `/ready` returning HTTP 503 Service Unavailable.

## 2. Immediate Actions
```bash
# 1. Check pod status in multi-agent-exam namespace
kubectl get pods -n multi-agent-exam -l app.kubernetes.io/name=exam-portal-backend

# 2. Inspect container logs for stack traces
kubectl logs -n multi-agent-exam -l app.kubernetes.io/name=exam-portal-backend --tail=100

# 3. Perform rolling restart if unrecoverable
kubectl rollout restart deployment/multi-agent-exam-portal-backend -n multi-agent-exam
```
