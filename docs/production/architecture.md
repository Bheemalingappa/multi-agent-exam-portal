# Production Kubernetes Architecture

## 1. Strategy Comparison

### Strategy A — Managed Cloud Infrastructure (Recommended for Production)
```
Kubernetes (EKS / GKE / AKS)
   │
   ├── FastAPI Deployment (HPA: 2-10 replicas)
   ├── Frontend Deployment (Nginx: 2-5 replicas)
   ├── Celery Worker Deployment (HPA: 2-8 replicas)
   │
   ├── Managed PostgreSQL (Amazon RDS / GCP Cloud SQL: Multi-AZ HA)
   └── Managed Redis (Amazon ElastiCache / GCP MemoryStore: Cluster Mode)
```
- **Pros**: Automated Multi-AZ failover, point-in-time recovery (PITR), managed backups, automated OS patching.

---

### Strategy B — In-Cluster Stateful Services
```
Kubernetes Cluster
   │
   ├── PostgreSQL StatefulSet (Primary + Replica PVCs)
   └── Redis StatefulSet (Sentinel HA)
```
- **Pros**: Zero cloud vendor lock-in, suitable for bare-metal or on-premises Kubernetes deployments.
