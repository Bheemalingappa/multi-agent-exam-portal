# CI/CD Pipeline Architecture & Automation Strategy

## 1. Overview
The **Multi-Agent Exam & Evaluation Portal** utilizes GitHub Actions for continuous integration, automated security scanning, container image validation, and deployment pipeline automation.

## 2. CI/CD Workflows (`.github/workflows/`)

```
Push / Pull Request
       │
 ┌─────┴──────────────────┬──────────────────┬──────────────────┐
 ▼                        ▼                  ▼                  ▼
ci.yml                 security.yml       docker.yml         e2e.yml
 - Python compileall    - Bandit AST scan  - Compose config   - Full stack init
 - Backend unittest     - Secret scan      - Image builds     - Health check
 - Frontend Vite build  - Dependency check
```

---

## 3. Workflow Specifications

### 1. `ci.yml` (Continuous Integration)
- Runs on Python 3.11 and Node 20 runner environments.
- Executes `python -m compileall backend/app`.
- Executes unit test discovery (`python -m unittest discover -s backend/tests`).
- Builds frontend production static assets (`cd frontend && npm run build`).

### 2. `security.yml` (Security Audit)
- Runs Bandit AST security linter against `backend/app`.
- Verifies `.env` environment secrets are excluded from Git repository index.

### 3. `docker.yml` (Container Image Verification)
- Validates multi-container topology using `docker compose config`.
- Executes production builds for `backend`, `frontend`, and `sandbox` containers.
