import argparse
import time
import httpx

def run_submission_load_test(host: str, candidates_count: int):
    print(f"--- Starting Celery Task Submission Benchmark: {candidates_count} candidates against {host} ---")
    latencies = []
    successes = 0
    failed = 0

    with httpx.Client(base_url=host, timeout=10.0) as client:
        start_time = time.time()
        for i in range(candidates_count):
            t0 = time.time()
            try:
                res = client.post(
                    "/api/v1/submissions",
                    json={
                        "language": "python",
                        "code": f"def solve(): return {i}\nprint(solve())"
                    }
                )
                dt = (time.time() - t0) * 1000
                if res.status_code in [200, 202]:
                    successes += 1
                    latencies.append(dt)
                else:
                    failed += 1
            except Exception:
                failed += 1

    total_time = time.time() - start_time
    latencies.sort()

    p50 = round(latencies[len(latencies) // 2], 2) if latencies else 0
    p95 = round(latencies[int(len(latencies) * 0.95)], 2) if latencies else 0

    print(f"--- Results ---")
    print(f"Submissions Ingested: {successes} | Failures: {failed} | Total Time: {round(total_time, 2)}s")
    print(f"Ingestion Latency: p50={p50}ms | p95={p95}ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--candidates", type=int, default=10)
    args = parser.parse_args()

    run_submission_load_test(args.host, args.candidates)
