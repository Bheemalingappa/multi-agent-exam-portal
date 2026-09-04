# Production Kubernetes & Helm Deployment Guide

## 1. Prerequisites
- `kubectl` v1.28+ connected to target Kubernetes cluster.
- `helm` v3.12+.
- `cert-manager` & `ingress-nginx` controller installed on cluster.

## 2. Deploying via Helm

```bash
# 1. Validate Helm Chart syntax
helm lint helm/multi-agent-exam-portal

# 2. Template dry-run verification
helm template multi-agent-exam helm/multi-agent-exam-portal

# 3. Deploy to Production Cluster
helm upgrade --install multi-agent-exam \
  helm/multi-agent-exam-portal \
  -n multi-agent-exam \
  --create-namespace \
  -f helm/multi-agent-exam-portal/values-production.yaml

# 4. Verify Rollout Status
kubectl rollout status deployment/multi-agent-exam-portal-backend -n multi-agent-exam
kubectl rollout status deployment/multi-agent-exam-portal-frontend -n multi-agent-exam
kubectl rollout status deployment/multi-agent-exam-portal-celery-worker -n multi-agent-exam
```
