# Production Architecture Specification & Cloud Infrastructure Topology

## 1. Reference Cloud Infrastructure (AWS)

```text
                               INTERNET
                                  │
                                  ▼
                         Route 53 (Global DNS)
                                  │
                         CloudFront (CDN + WAF)
                                  │
                       ALB / Nginx Ingress (TLS)
                                  │
             ┌────────────────────┴────────────────────┐
             ▼                                         ▼
   Frontend Pods (Nginx)                    FastAPI Gateway Pods
   (2 Replicas, Port 80)                    (2-10 Replicas, Port 8000)
                                                       │
                     ┌─────────────────────────────────┼─────────────────────────────────┐
                     ▼                                 ▼                                 ▼
           Amazon RDS PostgreSQL            Amazon ElastiCache Redis               Celery Worker Pods
           (Multi-AZ Engine v15)            (Cluster Engine v7)                    (2-16 Replicas, Docker SDK)
                                                                                             │
                                                                                             ▼
                                                                                   Ephemeral Docker Sandbox
                                                                                   (10001:10001, net=none)
```

---

## 2. Component Resource Specifications

1. **AWS EKS Cluster**: Managed Kubernetes v1.28 cluster with node groups across 3 Availability Zones.
2. **Amazon RDS PostgreSQL 15**: Multi-AZ instance with Write-Ahead Logging (WAL) streaming, 35-day automated backup retention (RPO < 5 min, RTO < 15 min), and TLS 1.3 encrypted connections.
3. **Amazon ElastiCache Redis 7**: Managed Redis instance providing task broker queues for Celery, dashboard caching, and real-time WebSocket Pub/Sub event broadcasting.
4. **AWS Secrets Manager**: Encrypted secret storage for database credentials, JWT secret keys, Redis connection URLs, and LLM API keys.
5. **AWS CloudFront & WAF**: Global CDN for static asset distribution with rate-limiting, SQL injection, and XSS protection rules.
