# Technical Achievements & Engineering Highlights

## 1. Artificial Intelligence (AI)
- **Multi-Lingual Question Synthesis**: Integrated Google Gemini 3.1 Flash Lite (`google-genai` SDK) to generate structured question papers in **English** and **Kannada**.
- **Source Material Modes**: Implemented 3 generation modes (`TOPIC_ONLY`, `PDF_ONLY`, `PDF_AND_TOPIC`) with strict topic isolation (`exact_topic`).
- **Verbatim Copy Prevention**: System prompts enforce conceptual synthesis from PDF materials rather than direct line extraction.
- **Fail-Fast Provider Integrity**: Errors raise explicit HTTP 503 exceptions without silent fallback to static template generation.

---

## 2. Backend Engineering
- **FastAPI Microservices**: Built asynchronous REST APIs with Pydantic validation and Uvicorn server.
- **Modular Routers**: Structured API routing across Auth, Question Papers, Exams, Attempts, Evaluation, and Analytics modules.
- **Clean Error Sanitization**: Exception middleware prevents SQL, stack traces, or credentials from leaking in API errors.

---

## 3. Frontend Development
- **React 18 + TypeScript**: Enforced static type safety across API client calls and UI state management.
- **Stateful Exam Workspace**: Implemented auto-saving answer buffers, floating server timer, and crash-resistant session resume.
- **Responsive Educator UI**: Interactive draft question editor, options modifier, section reordering, and analytics charts.

---

## 4. Database & Caching
- **PostgreSQL Relational Schema**: Modeled 1-to-many and 1-to-1 relationships across Users, QuestionPapers, Sections, Questions, Exams, Assignments, Attempts, Answers, and EvaluationResults.
- **Optimized SQL Aggregations**: Built single-query analytics aggregations (`COUNT`, `AVG`, `STDDEV`) avoiding N+1 performance issues.
- **Redis Caching**: Ephemeral caching for active candidate attempts, server timer calculations, and session tokens.

---

## 5. Security & Authorization
- **Role-Based Access Control (RBAC)**: JWT authentication isolating `recruiter` (Teacher) and `candidate` (Student) capabilities.
- **Class-Level Authorization**: Enforces grade matching (Classes 1–12); cross-grade attempt access returns `403 Forbidden`.
- **IDOR Protection**: Enforces explicit resource ownership checks on student attempts and teacher papers.
- **Answer-Key Sanitization**: Strips `correct_answer`, `solution`, `explanation`, and agent prompts from candidate API responses.
- **Server-Authoritative Timer**: Timer calculated server-side as $\text{expires\_at} - \text{now\_utc}()$.

---

## 6. Multi-Agent Evaluation Engine
- **Hybrid Grading Pipeline**:
  - MCQ: Deterministic exact string match (100% or 0%).
  - Short Answer: Rubric-guided keyword & semantic evaluation with partial credit.
  - Long Answer: Multi-agent consensus scoring.
- **Immutable Results**: Attempt locking on submit prevents post-submission answer modification.

---

## 7. Cloud Infrastructure & DevOps
- **Amazon EKS Deployment**: Orchestrated containerized deployment in Kubernetes namespace `multi-agent-exam` on AWS EKS.
- **Container Registry**: Built and pushed production container images to Amazon ECR (`:v46`).
- **Health Probes**: Configured Kubernetes `livenessProbe`, `readinessProbe`, and `startupProbe` on FastAPI pods.
- **Network Load Balancer**: Routed traffic through AWS NLB and Nginx ingress controller.

---

## 8. Testing & Quality Assurance
- **100% Automated Test Suite**: Built integration suites in `scratch/` (`test_phase47_final_qa.py`) validating E2E workflows, class security, IDOR, timer security, PDF security, analytics, and EKS health.
