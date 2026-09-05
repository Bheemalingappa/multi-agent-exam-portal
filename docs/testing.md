# Automated Testing & Verification Documentation

## Overview
The application incorporates a multi-phase automated test suite located in `scratch/`. Each test script runs end-to-end HTTP integration assertions directly against the active backend service.

---

## 1. Test Suite Matrix & Verification Summary

| Test File Path | Target Milestone / Verification Scope | Execution Status | Test Coverage |
| :--- | :--- | :---: | :--- |
| `scratch/test_phase41_source_architecture.py` | Live Gemini Question Generation Architecture | **PASS (100%)** | `TOPIC_ONLY`, `PDF_ONLY`, `PDF_AND_TOPIC`, `exact_topic` preservation, Kannada language, requested question counts. |
| `scratch/test_phase43_workflow.py` | Complete Teacher Examination Lifecycle | **PASS (100%)** | Draft creation, question editing, publishing, class assignment, catalog isolation, PDF render security. |
| `scratch/test_phase44_student_exam.py` | Student Exam-Taking, Timer & Security | **PASS (100%)** | Class-level start authorization, autosave, server-authoritative timer, attempt resume, submit locking, answer key protection. |
| `scratch/test_phase45_evaluation.py` | Multi-Agent Evaluation & Scoring Engine | **PASS (100%)** | MCQ exact match, Short answer partial credit, Long answer consensus, score/grade persistence, retry mechanism, candidate response sanitization. |
| `scratch/test_phase46_analytics.py` | Results, Performance & Teacher Analytics | **PASS (100%)** | Student summary, score trends, teacher summary, exam performance metrics, question difficulty table, sortable student roster, IDOR security. |
| `scratch/test_phase47_final_qa.py` | Phase 47 Final QA, Hardening & E2E Validation | **PASS (100%)** | All 22 QA areas: full 9-step E2E workflow, source modes, counts, languages, class security, IDOR, timer, immutability, evaluation, analytics, PDFs, error handling, DB integrity, EKS health. |

---

## 2. Running Automated Tests

To execute the full production verification suite against the active backend:

```bash
# Execute Phase 47 Complete Production QA Suite
python scratch/test_phase47_final_qa.py

# Execute Individual Regression Suites
python scratch/test_phase41_source_architecture.py
python scratch/test_phase43_workflow.py
python scratch/test_phase44_student_exam.py
python scratch/test_phase45_evaluation.py
python scratch/test_phase46_analytics.py
```

---

## 3. Key Assertions & Security Controls Tested

1. **Class-Level Authorization**:
   - Class 7 student $\rightarrow$ Allowed to start Class 7 exam.
   - Class 8 student $\rightarrow$ `403 Forbidden` on Class 7 exam catalog listing, details, attempt start, and answers save.

2. **IDOR Protection**:
   - Student B attempting to read Student A's attempt or evaluation result $\rightarrow$ `403 Forbidden`.
   - Teacher B attempting to read or edit Teacher A's draft question paper or exam analytics $\rightarrow$ `403 Forbidden`.

3. **Answer-Key Sanitization**:
   - Verifies that `GET /api/v1/attempts/{id}` responses for student accounts strictly omit `correct_answer`, `solution`, `explanation`, `teacher_rubric`, `agent_prompts`, and `security_findings`.

4. **Submission Immutability**:
   - Calling `POST /api/v1/attempts/{id}/submit` updates attempt status to `SUBMITTED`.
   - Subsequent `PUT /api/v1/attempts/{id}/answers` or duplicate `POST /api/v1/attempts/{id}/submit` requests strictly return `400 Bad Request`.

5. **Server-Authoritative Timer**:
   - Verification that remaining exam duration is calculated server-side as $\text{expires\_at} - \text{current\_utc\_time}$. Manipulating client-side system clock or refreshing the browser has zero effect.
