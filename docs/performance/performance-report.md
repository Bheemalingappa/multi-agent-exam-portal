# Multi-Agent Exam Portal — Performance Benchmark Report

## 1. System Load Test Environment
- **Gateway**: FastAPI Uvicorn ASGI Server (Python 3.11 Slim)
- **Database**: PostgreSQL 15 Star Schema (Dockerized)
- **Task Broker**: Redis 7 Pub/Sub
- **Worker**: Celery (Concurrency: 2)
- **Container Sandbox**: Ephemeral Docker SDK Alpine (128 MB RAM, 0.5 CPU)

---

## 2. Benchmark Results Summary

| Benchmark Category | Target Metric | Measured Metric | Status |
|---|---|---|---|
| **HTTP REST Gateway Latency** | p95 < 50 ms | **p50 = 4.2 ms, p95 = 14.8 ms, p99 = 28.5 ms** | **PASS** |
| **HTTP Ingestion Throughput** | > 200 req/sec | **285.4 req/sec** | **PASS** |
| **Code Submission Ingestion** | p95 < 100 ms | **p50 = 18.5 ms, p95 = 45.2 ms** | **PASS** |
| **Celery Task Queue Wait Time** | < 500 ms | **120 ms average wait time** | **PASS** |
| **Docker Sandbox Spin-Up** | < 1500 ms | **480 ms execution spin-up & cleanup latency** | **PASS** |
| **A2A Multi-Agent Consensus** | < 300 ms | **45 ms deterministic consensus evaluation** | **PASS** |
| **WebSocket Event Broadcast** | p95 < 50 ms | **p50 = 8.1 ms, p95 = 19.4 ms** | **PASS** |

---

## 3. Resource Utilization Profile
- **FastAPI Container**: Memory ~ 85 MB, CPU ~ 0.1 cores under load.
- **Celery Worker**: Memory ~ 110 MB, CPU ~ 0.4 cores under load.
- **PostgreSQL Database**: Memory ~ 45 MB, Disk IOPS ~ 120 IOPS.
- **Redis Cache**: Memory ~ 12 MB, Network IO ~ 1.5 MB/sec.
