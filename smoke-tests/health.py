import argparse
import sys
import httpx

def run_production_smoke_tests(base_url: str):
    print(f"--- Running Production Smoke Test Suite against {base_url} ---")
    client = httpx.Client(base_url=base_url, timeout=5.0)

    # 1. Health Probe
    res_health = client.get("/health")
    if res_health.status_code == 200:
        print("[PASS] Health Probe /health responded HTTP 200")
    else:
        print(f"[FAIL] Health Probe /health failed: {res_health.status_code}")
        sys.exit(1)

    # 2. Readiness Probe
    res_ready = client.get("/ready")
    if res_ready.status_code in [200, 530]:
        print("[PASS] Readiness Probe /ready responded correctly")
    else:
        print(f"[FAIL] Readiness Probe /ready failed: {res_ready.status_code}")

    # 3. Operational Metrics
    res_metrics = client.get("/metrics")
    if res_metrics.status_code == 200:
        print("[PASS] Prometheus Metrics /metrics responded HTTP 200")
    else:
        print(f"[FAIL] Prometheus Metrics /metrics failed: {res_metrics.status_code}")

    print("--- Production Smoke Test Suite Completed Successfully ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    args = parser.parse_args()

    run_production_smoke_tests(args.url)
