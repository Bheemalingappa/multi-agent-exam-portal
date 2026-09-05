# Security Architecture & Production Hardening Guide

## 1. Implemented Security Controls

The **Multi-Agent Exam & Evaluation Portal** incorporates multi-layered security controls covering authentication, role authorization, resource ownership, response sanitization, and infrastructure isolation.

### A. Authentication & JWT Tokens
- **Algorithm**: Standard JWT Bearer token authentication signed via HMAC SHA-256 (`HS256`).
- **Token Claims**: Contains user ID (`sub`), role (`recruiter` / `candidate`), and `class_level` (1–12).
- **Expiration**: Standard token expiration enforced on backend API requests.

### B. Role-Based Access Control (RBAC) & Class Authorization
- **Role Isolation**:
  - `recruiter` (Teacher): Granted permissions to generate questions, create/edit drafts, publish papers, assign exams, view answer keys, and access teacher analytics. Denied student attempt actions.
  - `candidate` (Student): Granted permissions to view class-filtered exam catalog, start attempts, autosave answers, submit attempts, and view personal evaluation results. Denied paper creation, answer key PDFs, and teacher analytics.
- **Class-Level Authorization**:
  - When an exam is assigned to `class_level = 7`, students with `class_level = 8` or `9` are strictly blocked (`403 Forbidden`) from viewing, starting, or submitting the exam.

### C. Resource Ownership & IDOR Protection
- **Teacher Ownership**: Teachers can only view, edit, publish, assign, or view analytics for question papers and exams they created. Cross-teacher requests return `403 Forbidden`.
- **Student Ownership**: Students can only access, save answers to, or view evaluation results for exam attempts tied to their user ID. Cross-student access returns `403 Forbidden`.

### D. Confidential Answer-Key & Prompt Protection
- **Candidate API Sanitization**: All candidate-facing API endpoints (`GET /api/v1/attempts/{id}`) sanitize out correct answers, solutions, explanations, teacher rubrics, and internal agent prompts.
- **PDF Authorization**:
  - Student Printable Question Paper PDF (`GET /api/v1/question-papers/{id}/pdf`): Contains questions, options, instructions, duration, and maximum marks; strictly omits answers and solutions.
  - Teacher Official Answer Key PDF (`GET /api/v1/question-papers/{id}/answer-key-pdf`): Candidate access returns `403 Forbidden`.

### E. Server-Authoritative Timer & Submission Immutability
- **Timer Security**: Remaining time is calculated server-side as $\text{remaining\_seconds} = \text{expires\_at} - \text{now\_utc}()$. Client-side system clock manipulation or page refreshing cannot extend exam time.
- **Attempt Locking**: Submitting an attempt changes status to `SUBMITTED`. Any subsequent answer modifications (`PUT /api/v1/attempts/{id}/answers`) or duplicate submissions return `400 Bad Request`.

### F. API Error Sanitization & Secret Isolation
- Standardized FastAPI exception handlers prevent database stack traces, SQL strings, or credentials (`postgresql://`, `redis://`, API keys) from being exposed in error JSON payloads.

---

## 2. Production Security Recommendations (Future Roadmap)

While current security controls meet all functional requirements, the following infrastructure enhancements are recommended for enterprise production hardening:

1. **HTTPS / TLS Termination**: Terminate TLS 1.3 at AWS ALB / NLB using AWS Certificate Manager (ACM).
2. **AWS WAF Integration**: Attach AWS WAF to the ingress Load Balancer to protect against OWASP Top 10 web vulnerabilities (SQL injection, XSS, rate limiting).
3. **AWS Secrets Manager**: Transition database passwords, JWT secrets, and Gemini API keys from Kubernetes Secrets to AWS Secrets Manager with automatic secret rotation.
4. **Audit Logging & Telemetry**: Stream immutable application and audit logs to Amazon CloudWatch / AWS CloudTrail.
5. **Network Policies**: Enforce strict Kubernetes `NetworkPolicy` objects restricting pod-to-pod communication within the EKS namespace.
