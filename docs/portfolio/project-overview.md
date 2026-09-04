# Multi-Agent Exam & Evaluation Portal — Executive Overview

## 1. System Summary
The **Multi-Agent Exam & Evaluation Portal** is a production-grade, highly secure technical assessment platform featuring ephemeral Docker sandbox virtualization, multi-agent AI evaluation (Mentor, QA, Security, Performance), A2A consensus negotiation, AST structural plagiarism detection, real-time WebSockets, KEDA worker autoscaling, and enterprise identity (OIDC/SAML/SCIM).

## 2. Core Architectural Principles
- **Sandbox Security**: Non-root `10001:10001`, `network_mode="none"`, `read_only=True`, 128MB RAM limit, 0.5 CPU quota.
- **AI Safety & Circuit Breaker**: Deterministic fallback prevents LLM outages from corrupting candidate scores.
- **Enterprise Multi-Tenancy**: Organization boundaries enforced across all API endpoints, vector embeddings, and audit trails.
