# Multi-Agent Exam Portal — Load Testing Suite

Load testing scripts for evaluating system throughput under concurrent candidate loads.

## Prerequisites

Install optional load testing dependencies:
```bash
pip install locust httpx
```

## Running Load Tests

To simulate concurrent candidate submissions and WebSocket event consumption:

```bash
# Run 50 concurrent virtual candidates
python load_tests/submission_load.py --candidates 50 --host http://localhost:8000
```

## Metrics Measured

- HTTP API Submission Ingestion Latency (ms)
- WebSocket Handshake & Event Delivery Latency (ms)
- Celery Task Pipeline Queue Throughput
- Docker Sandbox Ephemeral Container Creation / Cleanup Rate
- PostgreSQL Query Latency under Concurrent Read/Write Load
