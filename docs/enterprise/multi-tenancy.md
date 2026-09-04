# Enterprise Multi-Tenancy & Tenant Isolation

## 1. Organization Boundary
- All platform resources (exams, questions, attempts, submissions, analytics, audit events) enforce strict `organization_id` isolation.
- Cross-tenant vector query retrieval or plagiarism comparison attempts are rejected by database foreign key bounds and API authorization guards.
