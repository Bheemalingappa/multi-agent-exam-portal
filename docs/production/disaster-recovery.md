# Disaster Recovery & RPO/RTO Targets

## 1. Service Level Objectives (SLOs)
- **Recovery Point Objective (RPO)**: < 5 Minutes (PostgreSQL Write-Ahead Logging WAL streaming).
- **Recovery Time Objective (RTO)**: < 15 Minutes (Automated Kubernetes deployment & Multi-AZ RDS failover).
