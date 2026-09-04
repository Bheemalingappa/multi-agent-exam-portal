# Service Level Objectives (SLOs) & Error Budget Burn Rates

## 1. Measurable SLO Targets

| Service Component | Target Metric | Target Threshold | Error Budget Window |
|---|---|---|---|
| **FastAPI Gateway Availability** | Availability % | **99.9% Target** | 43.8 minutes / month |
| **HTTP REST Response Latency** | Latency p95 | **< 50 ms Target** | N/A |
| **Celery Submission Evaluation** | Pipeline Success % | **99.5% Target** | 0.5% failure budget |
| **WebSocket Delivery Latency** | Broadcast Latency p95 | **< 50 ms Target** | N/A |
