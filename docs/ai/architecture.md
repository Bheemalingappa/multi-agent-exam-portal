# Production AI & Agent Architecture

## 1. Overview
The Phase 9 Production AI Architecture enriches candidate evaluation with structured LLM scoring (Gemini 1.5 Pro), RAG semantic code retrieval, MCP context injection, and evidence-first A2A consensus negotiation.

```
Candidate Code ──► Ephemeral Sandbox ──► Hidden Test Execution ──► AST Pre-Screen
                                                                        │
                                                                        ▼
                                                             RAG & MCP Context
                                                                        │
                                                                        ▼
                                                             Multi-Agent System
                                                       (Mentor, QA, Security, Perf)
                                                                        │
                                                                        ▼
                                                             A2A Consensus Engine
                                                                        │
                                                                        ▼
                                                             Human Recruiter Override
```
