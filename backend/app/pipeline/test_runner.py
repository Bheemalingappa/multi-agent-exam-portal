import hashlib
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from app.database.models import TestCase, TestResult, SubmissionFact
from app.pipeline.sandbox import DockerSandboxEngine
from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_OUTPUT_BYTES = 65536  # 64 KB maximum stdout capture limit

class HiddenTestRunner:
    """
    Server-side engine for executing candidate code against hidden test cases.
    Performs output normalization, stdout size caps, expected output hashing, and functional scoring.
    """

    @staticmethod
    def normalize_output(text: str) -> str:
        """Normalizes line endings (CRLF -> LF) and strips surrounding whitespace."""
        if not text:
            return ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        return normalized.strip()

    @classmethod
    def execute_test_cases(
        cls,
        db: Session,
        submission: SubmissionFact,
        test_cases: List[TestCase],
        sandbox_engine: DockerSandboxEngine
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Executes candidate code against test cases, persists fact_test_results,
        and calculates functional score percentage (0-100).
        """
        if not test_cases:
            logger.info("No test cases defined for question; defaulting functional score to 100.0.")
            return 100.0, []

        total_weight = sum(float(tc.weight) for tc in test_cases)
        passed_weight = 0.0
        results = []

        for tc in test_cases:
            tc_id = str(tc.id)
            expected_output_clean = cls.normalize_output(tc.expected_output)
            expected_hash = hashlib.sha256(expected_output_clean.encode("utf-8")).hexdigest()

            # Construct execution wrapper feeding test input via sys.stdin
            input_sanitized = tc.input_data.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            wrapped_code = (
                "import sys, io\n"
                f"sys.stdin = io.StringIO(\"{input_sanitized}\")\n"
                f"{submission.source_code}\n"
            )

            # Run in ephemeral sandbox
            sandbox_res = sandbox_engine.run_code(
                code=wrapped_code,
                mem_limit=settings.SANDBOX_MEM_LIMIT,
                cpu_quota=settings.SANDBOX_CPU_QUOTA,
                timeout_seconds=int(tc.timeout_seconds)
            )

            actual_stdout = sandbox_res.get("stdout", "")
            actual_stderr = sandbox_res.get("stderr", "")
            exit_code = sandbox_res.get("exit_code", 0)
            latency = sandbox_res.get("execution_latency_ms", 0.0)
            memory = sandbox_res.get("peak_memory_mb", 0.0)

            # Output size limit enforcement
            if len(actual_stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
                tc_status = "OUTPUT_LIMIT_EXCEEDED"
                actual_stdout = actual_stdout[:1000] + "\n...[TRUNCATED: Output limit exceeded]"
                err_msg = "Output limit exceeded (max 64KB allowed)."
                score_awarded = 0.0
            elif sandbox_res.get("security_violation"):
                tc_status = "SECURITY_BLOCKED"
                err_msg = actual_stderr
                score_awarded = 0.0
            elif sandbox_res.get("timed_out"):
                tc_status = "TIMEOUT"
                err_msg = "Test case execution timed out."
                score_awarded = 0.0
            elif exit_code != 0:
                tc_status = "RUNTIME_ERROR"
                err_msg = actual_stderr or f"Non-zero exit code {exit_code}"
                score_awarded = 0.0
            else:
                actual_clean = cls.normalize_output(actual_stdout)
                if actual_clean == expected_output_clean:
                    tc_status = "PASSED"
                    err_msg = None
                    score_awarded = float(tc.weight)
                    passed_weight += float(tc.weight)
                else:
                    tc_status = "FAILED"
                    err_msg = "Output mismatch."
                    score_awarded = 0.0

            # Store test result record
            test_result = TestResult(
                submission_id=submission.submission_id,
                test_case_id=tc.id,
                status=tc_status,
                execution_latency_ms=latency,
                peak_memory_mb=memory,
                exit_code=exit_code,
                actual_output=actual_stdout if not tc.is_hidden else "[HIDDEN TEST CASE OUTPUT REDACTED]",
                expected_output_hash=expected_hash,
                error_message=err_msg,
                score_awarded=score_awarded
            )
            db.add(test_result)

            results.append({
                "test_case_id": tc_id,
                "order": tc.test_case_order,
                "is_hidden": tc.is_hidden,
                "status": tc_status,
                "latency_ms": latency,
                "memory_mb": memory,
                "score_awarded": score_awarded
            })

        db.commit()

        functional_score = round((passed_weight * 100.0) / max(total_weight, 1.0), 2)
        logger.info(f"Functional evaluation completed. Passed {passed_weight}/{total_weight} weight. Score: {functional_score}%")

        return functional_score, results
