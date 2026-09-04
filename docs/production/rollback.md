# Helm & Kubernetes Deployment Rollback Guide

## 1. Rolling Back Helm Release

```bash
# 1. Check release revision history
helm history multi-agent-exam -n multi-agent-exam

# 2. Rollback to previous release revision
helm rollback multi-agent-exam <REVISION_NUMBER> -n multi-agent-exam

# 3. Verify Rollout Status
kubectl rollout status deployment/multi-agent-exam-portal-backend -n multi-agent-exam
```
