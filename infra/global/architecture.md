# Multi-Region & Global Infrastructure Architecture

## 1. Global Topology
- **Primary Region (Region A - us-east-1)**: Hosts primary FastAPI Kubernetes cluster, Celery task workers, and PostgreSQL Primary instance.
- **Secondary Region (Region B - us-west-2)**: Hosts secondary standby Kubernetes cluster and PostgreSQL Read Replica.

```
                         GLOBAL USERS
                              │
                              ▼
                       Global Anycast DNS
                              │
                     Cloud CDN (Static Assets)
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
        Region A (Primary)            Region B (Standby)
        us-east-1                     us-west-2
               │                             │
        FastAPI Gateway               FastAPI Standby
               │                             │
     PostgreSQL Primary ──(Replication)──► PostgreSQL Replica
```
