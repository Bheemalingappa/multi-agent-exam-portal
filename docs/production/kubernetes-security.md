# Kubernetes Security & Docker Socket Risk Analysis

## 1. Security Context Controls
- **Non-Root Execution**: FastAPI Gateway and Frontend run under UID `10001:10001`.
- **Privilege Escalation**: `allowPrivilegeEscalation: false` with all Linux capabilities dropped (`cap_drop=["ALL"]`).
- **Network Isolation**: Namespace NetworkPolicies enforce deny-all by default.

---

## 2. Docker Socket Mount Risk & Mitigation
- **Risk**: Mounting `/var/run/docker.sock` onto `celery_worker` provides host-equivalent Docker Engine control.
- **Mitigation**: Dedicated node pool isolation for Celery worker nodes, restricting socket access strictly to worker pods, or replacing Docker SDK with gVisor / Kata / Kubernetes Job ephemeral runners for future multi-tenant cluster expansions.
