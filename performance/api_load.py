import argparse
import time
import httpx

def benchmark_api(host: str, concurrency: int):
    print(f"--- Starting API Benchmark: {concurrency} concurrent requests to {host} ---")
    latencies = []
    successes = 0
    failures = 0

    with httpx.Client(base_url=host, timeout=5.0) as client:
        start_all = time.time()
        for i in range(concurrency):
            t0 = time.time()
            try:
                res = client.get("/health")
                dt = (time.time() - t0) * 1000
                if res.status_code == 200:
                    successes += 1
                    latencies.append(dt)
                else:
                    failures += 1
            except Exception:
                failures += 1

    total_time = time.time() - start_all
    latencies.sort()

    p50 = round(latencies[len(latencies) // 2], 2) if latencies else 0
    p95 = round(latencies[int(len(latencies) * 0.95)], 2) if latencies else 0
    p99 = round(latencies[int(len(latencies) * 0.99)], 2) if latencies else 0

    print(f"--- Results ---")
    print(f"Total Requests: {concurrency} | Successful: {successes} | Failures: {failures}")
    print(f"Latency: p50={p50}ms | p95={p95}ms | p99={p99}ms")
    print(f"Throughput: {round(successes / max(total_time, 0.01), 2)} req/sec")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--concurrency", type=int, default=50)
    args = parser.parse_args()

    benchmark_api(args.host, args.concurrency)
