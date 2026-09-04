# Performance Engineering & High-Concurrency Benchmark Suite

High-throughput load testing scripts designed to measure API response latency, Celery task queue throughput, Docker sandbox spin-up rates, and WebSocket event delivery latency.

## Load Test Tools

1. **`api_load.py`**: Benchmarks REST endpoints (`/auth/login`, `/exams`, `/submissions`, `/analytics`) under concurrent HTTP load.
2. **`websocket_load.py`**: Benchmarks concurrent WebSocket connections and event delivery.
3. **`submission_load.py`**: Benchmarks full end-to-end Celery evaluation task pipeline.

## Running Benchmarks

```bash
# REST API Benchmark (50 concurrent users)
python performance/api_load.py --concurrency 50 --host http://localhost:8000

# WebSocket Load Test (50 concurrent sockets)
python performance/websocket_load.py --connections 50 --host ws://localhost:8000

# End-to-End Submission Pipeline Load Test
python performance/submission_load.py --candidates 50 --host http://localhost:8000
```
