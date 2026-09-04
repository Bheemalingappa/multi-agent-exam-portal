# Multi-Agent AI & A2A Consensus Case Study

## 1. Multi-Agent System Architecture
- **Mentor Agent**: Evaluates code readability, structural design, and algorithm maintainability.
- **QA Agent**: Evaluates functional correctness, edge case handling, and test case coverage.
- **Security Agent**: Scans for hardcoded credentials, AST dangerous patterns, and prompt injection vulnerabilities.
- **A2A Consensus Engine**: Reconciles individual agent scores over up to `MAX_A2A_ROUNDS=3` negotiation rounds to compute a unified consensus score and confidence score.
