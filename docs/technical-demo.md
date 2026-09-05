# 5-Minute Technical Demonstration Outline

## Overview
This document provides a structured 5-minute technical demonstration outline for deep-dive engineering interviews and system architecture reviews.

---

## Technical Agenda & File Inspection Index

| Time | Agenda Topic | Technical Focus & Code Files to Show | Key Architectural Concepts |
| :--- | :--- | :--- | :--- |
| `0:00 - 0:45` | **1. System Architecture & Cloud Infrastructure** | Inspect `docs/architecture.md`, `k8s/`, `docs/deployment.md`. | AWS EKS, Nginx Ingress, AWS NLB, Amazon ECR `:v46` images, PostgreSQL RDS, ElastiCache Redis. |
| `0:45 - 1:30` | **2. AI Question Generation Engine** | Inspect `backend/app/ai/gemini_question_provider.py`, `backend/app/api/question_papers.py`. | Google Gemini 3.1 Flash Lite API (`google-genai`), Pydantic schema validation, `exact_topic` isolation, Kannada text synthesis. |
| `1:30 - 2:15` | **3. Exam Lifecycle & Attempt Engine** | Inspect `backend/app/api/exams.py`, `backend/app/api/attempts.py`. | Draft $\rightarrow$ Publish $\rightarrow$ Assign state machine, background autosave, crash-resistant resume. |
| `2:15 - 3:00` | **4. Class & IDOR Security Controls** | Inspect `backend/app/core/security.py`, `backend/app/api/attempts.py`. | Class-level authorization (`class_level`), RBAC (`recruiter` vs `candidate`), IDOR ownership checks, candidate response sanitization. |
| `3:00 - 3:45` | **5. Multi-Agent Evaluation Engine** | Inspect `backend/app/services/evaluation_service.py`, `backend/app/agents/provider.py`. | MCQ exact match, short answer rubric evaluation, long answer multi-agent consensus, partial credit math. |
| `3:45 - 4:30` | **6. Analytics Engine & Performance** | Inspect `backend/app/analytics/service.py`, `backend/app/api/analytics.py`. | Aggregated SQL queries, itemized question difficulty rating (`Easy`/`Medium`/`Hard`), performance rosters. |
| `4:30 - 5:00` | **7. Automated Verification & Test Coverage** | Inspect `scratch/test_phase47_final_qa.py`. | 100% verified E2E and security regression test suite execution. |
