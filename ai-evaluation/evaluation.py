import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import json
from app.agents.fallback import DeterministicFallbackProvider

def run_golden_evaluation_benchmark():
    print("--- Starting MLOps Golden Dataset Evaluation Benchmark ---")
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "mlops", "golden", "golden_dataset.json")
    
    if not os.path.exists(dataset_path):
        print(f"Golden dataset not found at {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    provider = DeterministicFallbackProvider()
    passed = 0

    for case in cases:
        res = provider.evaluate("MENTOR", case["code"], case["name"], {"exit_code": 0, "execution_latency_ms": 10.0, "peak_memory_mb": 2.0})
        if res["score"] >= case["expected_min_score"]:
            passed += 1
            print(f"[PASS] Case '{case['case_id']}' Passed: Score {res['score']}")
        else:
            print(f"[FAIL] Case '{case['case_id']}' Failed: Score {res['score']}")

    print(f"--- Benchmark Results: {passed}/{len(cases)} cases passed cleanly ---")

if __name__ == "__main__":
    run_golden_evaluation_benchmark()
