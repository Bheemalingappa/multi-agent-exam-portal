# Attack Surface Analysis

## 1. External Entry Points
1. **REST API Gateway (`http://localhost:8000/api/v1`)**:
   - `/auth/login`, `/auth/register`: Public authentication endpoints. Rate limiting & bcrypt password hashing required.
   - `/submissions`: Accepts untrusted Python source code up to 100 KB payload limit (`MAX_SOURCE_CODE_BYTES`).
   - `/attempts/{id}/telemetry`: Accepts proctoring telemetry arrays (capped at 1000 items).
2. **WebSocket Gateway (`ws://localhost:8000/api/v1/ws`)**:
   - `/ws/exams/{attempt_id}`: Real-time exam connection requiring query param JWT authentication and IDOR ownership check.
   - `/ws/submissions/{submission_id}`: Real-time pipeline status stream.
3. **Model Context Protocol (MCP)**:
   - Evaluates file paths. Path traversal protection enforces `sanitize_path()` rejecting `..` or absolute paths (`/etc/passwd`).

---

## 2. Security Boundaries & Controls Matrix

| Boundary | Control Mechanism | Status |
|---|---|---|
| **Authentication** | Bcrypt password hashing + JWT HS256 access tokens (1440 min expiry) | VERIFIED |
| **Authorization** | Role-Based Access Control (RBAC) + Candidate IDOR ownership validation | VERIFIED |
| **Code Execution** | Ephemeral Docker Sandbox (`10001:10001`, `read_only=True`, `network="none"`, 128MB RAM, 0.5 CPU) | VERIFIED |
| **Static Pre-Screen** | AST static scanner throwing `ValueError` for prohibited imports (`os`, `subprocess`, `ctypes`, `socket`) | VERIFIED |
| **Data Protection** | Hidden test cases expected outputs protected; `CandidateQuestionResponseSchema` hides expected output | VERIFIED |
| **Prompt Injection** | AI Agents consume code as untrusted text within strict Pydantic schemas; fallback provider used if parsing fails | VERIFIED |
