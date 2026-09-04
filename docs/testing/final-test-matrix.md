# Master System Test Verification Matrix

| Test ID | Test Category | Target Component | Scenario / Expected Behavior | Measured Result | Status | Environment |
|---|---|---|---|---|---|---|
| **TEST-01** | E2E Workflow | `test_full_workflow.py` | Complete candidate-to-recruiter evaluation lifecycle | Complete pipeline executed cleanly | **PASS** | Staging / Local |
| **TEST-02** | Code Execution | `test_code_scenarios.py` | Correct code output normalized | Match expected output "42" | **PASS** | Staging / Local |
| **TEST-03** | Security Scan | `test_code_scenarios.py` | AST pre-screener rejects `import subprocess` | `ValueError` raised cleanly | **PASS** | Staging / Local |
| **TEST-04** | Output Cap | `test_code_scenarios.py` | 70 KB output truncated to 64 KB limit | Output truncated to 65,536 bytes | **PASS** | Staging / Local |
| **TEST-05** | Plagiarism | `test_code_scenarios.py` | Compare structurally identical functions | Similarity = 100%, Risk = HIGH | **PASS** | Staging / Local |
| **TEST-06** | Prompt Injection | `test_code_scenarios.py` | System prompt comment injection attempt | Treated as untrusted text string | **PASS** | Staging / Local |
| **TEST-07** | IDOR Security | `test_multi_tenant_idor.py` | Candidate A attempts to view Candidate B's submission | Cross-user access denied | **PASS** | Staging / Local |
| **TEST-08** | Multi-Tenancy | `test_multi_tenant_idor.py` | Org A attempts to access Org B resource | Tenant boundary access denied | **PASS** | Staging / Local |
| **TEST-09** | MLOps Evaluation| `evaluation.py` | Golden dataset regression benchmark (2 cases) | 2/2 cases passed cleanly | **PASS** | Staging / Local |
| **TEST-10** | Sandbox Isolation| `test_sandbox.py` | Execution runs under `10001:10001`, `net=none`, `read_only=True` | Sandbox constraints enforced | **PASS** | Container Environment |
