# Operational Runbook: Sandbox Execution Failure

## 1. Symptoms & Impact
- Submissions failing with `SANDBOX_ERROR` or Celery tasks failing to communicate with Docker daemon socket `/var/run/docker.sock`.

## 2. Immediate Mitigation
```bash
# Force cleanup orphaned sandbox containers
docker rm -f $(docker ps -a -q --filter ancestor=multi-agent-exam-portal-sandbox:latest)

# Restart Celery task worker deployment
kubectl rollout restart deployment/multi-agent-exam-portal-celery-worker -n multi-agent-exam
```
