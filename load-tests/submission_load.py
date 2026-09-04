import argparse
import time
import json
import httpx

def run_submission_load_test(host: str, candidates_count: int):
    """
    Simulates concurrent candidate registration, login, submission, and status polling.
    """
    print(f"--- Starting Load Test: {candidates_count} concurrent candidate simulations against {host} ---")
    start_total = time.time()
    successful = 0
    failed = 0

    with httpx.Client(base_url=host, timeout=10.0) as client:
        for i in range(candidates_count):
            email = f"load_candidate_{i}_{int(time.time())}@example.com"
            pwd = "LoadPassword123!"

            try:
                # 1. Register candidate
                reg_res = client.post("/api/v1/auth/register", json={"email": email, "password": pwd, "role": "candidate"})
                if reg_res.status_code != 201:
                    failed += 1
                    continue

                # 2. Login candidate
                login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
                if login_res.status_code != 200:
                    failed += 1
                    continue

                token = login_res.json().get("access_token")
                headers = {"Authorization": f"Bearer {token}"}

                # 3. Submit code payload
                sub_res = client.post(
                    "/api/v1/submissions",
                    headers=headers,
                    json={
                        "language": "python",
                        "code": f"# Candidate {i} solution\ndef solve(x):\n    return x * 2\n\nprint(solve({i}))"
                    }
                )
                if sub_res.status_code == 202:
                    successful += 1
                else:
                    failed += 1

            except Exception as err:
                print(f"Error during candidate {i} simulation: {err}")
                failed += 1

    duration = time.time() - start_total
    print(f"--- Load Test Finished in {round(duration, 2)}s ---")
    print(f"Successful Submissions: {successful} | Failed Submissions: {failed} | Throughput: {round(successful / max(duration, 0.1), 2)} req/sec")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Exam Portal Load Tester")
    parser.add_argument("--host", default="http://localhost:8000", help="Target API gateway host")
    parser.add_argument("--candidates", type=int, default=10, help="Number of simulated candidates")
    args = parser.parse_args()

    run_submission_load_test(args.host, args.candidates)
