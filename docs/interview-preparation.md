# Technical Interview Preparation — 25 Architectural Questions & Answers

## 1. Core Project & System Design

### Q1: Explain the overall architecture of the project.
**Answer**: EduExam is a cloud-native K-12 examination platform built with a FastAPI Python backend and React + TypeScript frontend deployed on AWS EKS. It decouples AI Question Generation (using Google Gemini 3.1 Flash Lite) from Student Answer Evaluation (using a backend Multi-Agent consensus engine). Persistence is backed by Amazon RDS PostgreSQL and caching by Amazon ElastiCache Redis.

### Q2: Why did you choose FastAPI for the backend framework?
**Answer**: FastAPI provides asynchronous request handling via Python `asyncio` and Uvicorn, native request/response validation through Pydantic schemas, automatic OpenAPI documentation, and high performance suitable for concurrent student exam submissions and real-time analytics aggregation.

### Q3: Why React with TypeScript for the frontend?
**Answer**: TypeScript enforces static type safety across API request/response models, preventing runtime errors in complex UI states like stateful exam countdown timers, auto-saving answer buffers, question draft editors, and interactive analytics charts.

### Q4: Why did you use PostgreSQL for application data?
**Answer**: PostgreSQL provides ACID compliance, strong relational integrity (foreign keys between Users, QuestionPapers, Exams, ExamAssignments, CandidateAttempts, and EvaluationResults), robust JSONB querying for structured question sections, and scalable aggregation support for analytics.

### Q5: What role does Redis play in the architecture?
**Answer**: ElastiCache Redis provides fast key-value caching for active candidate attempt state, server-side timer tracking, rate limiting, and session caching to minimize database load during simultaneous exam sessions.

---

## 2. AI Question Generation & Source Materials

### Q6: Why did you choose Google Gemini for question generation?
**Answer**: Google Gemini (via `google-genai` SDK) offers strong multi-lingual generation capabilities (English & Kannada), fast response times (~1-2 seconds with `gemini-3.1-flash-lite`), strict JSON schema enforcement, and cost-efficient structured text synthesis.

### Q7: How does structured question paper generation work under the hood?
**Answer**: The backend constructs a structured prompt specifying class level, subject, target topic (`exact_topic`), difficulty, language, and desired section configurations (MCQ, Short Answer, Long Answer). Gemini generates a JSON object adhering to Pydantic models.

### Q8: How does PDF-based question generation (`PDF_ONLY` / `PDF_AND_TOPIC`) work?
**Answer**: Uploaded PDFs are parsed to extract raw page text. In `PDF_ONLY` mode, questions are generated directly from the context. In `PDF_AND_TOPIC` mode, the PDF provides context/knowledge while `exact_topic` focuses what concept is tested.

### Q9: How do you prevent Gemini from simply copying PDF text verbatim?
**Answer**: System prompts explicitly instruct Gemini to analyze the context for core conceptual understanding and synthesize new, original educational questions rather than extracting text lines directly.

### Q10: How does the system handle Gemini API failures or quota limits?
**Answer**: The backend catches `APIError` or network exceptions from `google.genai.errors` and returns an explicit `503 Service Unavailable` response. When `AI_PROVIDER=gemini` is configured, it never silently falls back to dummy question papers.

---

## 3. Multi-Agent Evaluation & Scoring

### Q11: How does the Multi-Agent evaluation engine evaluate student answers?
**Answer**: Submitted answers pass through a routing pipeline based on question type:
- **MCQ**: Evaluated via exact-string matching against correct answers (100% or 0% marks).
- **Short Answer**: Evaluated using keyword and semantic rubric matching with partial credit support.
- **Long Answer**: Evaluated by a multi-agent consensus workflow assessing factual correctness, structural completeness, and clarity.

### Q12: How is partial marking implemented and bounded?
**Answer**: The evaluation engine computes partial marks per question such that $0 \le \text{awarded\_marks} \le \text{question\_marks}$. Total score is calculated as $\sum \text{awarded\_marks}$, capped at $\text{maximum\_marks}$, with percentage calculated as $\frac{\text{total\_score}}{\text{maximum\_score}} \times 100$.

### Q13: Are evaluation results immutable once computed?
**Answer**: Yes. When a student submits an attempt, status changes to `SUBMITTED` and evaluation results are persisted in `evaluation_results`. Subsequent evaluate requests are idempotent and return the persisted score unless forced by an authorized teacher retry.

---

## 4. Security, Authorization & Timer Integrity

### Q14: How is class-level authorization enforced?
**Answer**: User JWT tokens contain `role` and `class_level` (e.g., Class 7). When an exam is assigned to Class 7, backend endpoints (`POST /api/v1/exams/{id}/attempts`) verify student `class_level == assignment.class_level`. Cross-class attempts return `403 Forbidden`.

### Q15: How do you prevent Insecure Direct Object References (IDOR)?
**Answer**: Every attempt or analytics endpoint verifies resource ownership. A candidate can only fetch attempts where `attempt.candidate_id == current_user.id`. A teacher can only access question papers and exam analytics where `exam.created_by == current_user.id`. Unauthorized access returns `403 Forbidden`.

### Q16: How are answer keys protected from student tampering?
**Answer**: Candidate API responses (`GET /api/v1/attempts/{id}`) sanitize out `correct_answer`, `solution`, `explanation`, `teacher_rubric`, and agent prompts. Candidates attempting to access Answer Key PDFs receive `403 Forbidden`.

### Q17: How is the exam timer made server-authoritative?
**Answer**: When an attempt starts, `started_at` and `expires_at` are written to PostgreSQL. On every answer save or resume request, `remaining_seconds` is calculated server-side as $\text{expires\_at} - \text{now\_utc}()$. Client-side system clock manipulation or page refreshing cannot extend exam time.

### Q18: What prevents duplicate answer submissions after exam completion?
**Answer**: Submitting an attempt transitions its DB status to `SUBMITTED`. Attempt endpoints check status prior to executing updates; any `PUT /api/v1/attempts/{id}/answers` on a `SUBMITTED` or `EVALUATED` attempt returns `400 Bad Request`.

---

## 5. Analytics, Database & Cloud Infrastructure

### Q19: How are real-time analytics queries optimized?
**Answer**: Analytics queries in `AnalyticsService` use SQL aggregations (`COUNT`, `AVG`, `MAX`, `MIN`, `STDDEV`), JOINs across indexed foreign keys (`exam_id`, `candidate_id`, `created_by`), and filter on `exact_topic` directly, eliminating N+1 query loops.

### Q20: Why did you choose AWS EKS for container orchestration?
**Answer**: AWS EKS provides managed Kubernetes control planes, seamless integration with Amazon ECR for container image storage, fine-grained RBAC, native integration with AWS Load Balancers (NLB), and declarative deployment via standard Kubernetes manifests.

### Q21: How are secrets managed in production?
**Answer**: Database credentials, JWT signing keys, and Gemini API keys are injected via Kubernetes Secrets and ConfigMaps into container environment variables. `.env` files and real credentials are excluded from Git repository tracking.

### Q22: What HTTP status codes does the API return for error conditions?
**Answer**:
- `401 Unauthorized`: Missing or invalid JWT token.
- `403 Forbidden`: Role mismatch, wrong class level, or IDOR violation.
- `404 Not Found`: Non-existent exam, attempt, or paper ID.
- `400 Bad Request`: Invalid payload or modifying submitted attempts.
- `503 Service Unavailable`: External AI API failure.

### Q23: How do you verify database relational integrity?
**Answer**: SQLAlchemy models enforce foreign key constraints (`ForeignKey("users.id")`, `ForeignKey("question_papers.id")`), cascading deletes where appropriate, and 1-to-1 unique constraints between `CandidateAttempt` and `EvaluationResult`.

### Q24: How would you scale this application to handle 100,000 simultaneous students?
**Answer**:
1. Implement Horizontal Pod Autoscaling (HPA) for backend FastAPI pods based on CPU/memory metrics.
2. Enable RDS read replicas for student catalog and analytics queries.
3. Offload PDF generation and multi-agent long-answer evaluation to asynchronous Celery worker queues backed by Redis/SQS.
4. CDN caching (Amazon CloudFront) for static React assets.

### Q25: What future improvements would you prioritize next?
**Answer**: HTTPS termination at ALB via AWS ACM, AWS WAF integration for bot and DDoS protection, automated CI/CD pipeline via GitHub Actions, and centralized secret rotation via AWS Secrets Manager.
