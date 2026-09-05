# Resume Content & Technical Summary Bullet Points

## 1. Project Header & Technology Line
**PROJECT**: Multi-Agent Exam & Evaluation Portal (EduExam)  
**TECHNOLOGIES**: Python, FastAPI, React 18, TypeScript, Google Gemini 3.1 Flash Lite API, PostgreSQL, Redis, Docker, Kubernetes (AWS EKS), AWS NLB, Tailwind CSS.

---

## 2. One-Line Project Summary
> Developed and deployed an AI-powered K-12 examination and evaluation platform on AWS EKS, featuring Google Gemini multi-lingual question generation, multi-agent automated grading, server-authoritative timers, and real-time teacher analytics.

---

## 3. Four Strongest Engineering Resume Bullets

- **Production Cloud Architecture**: Built and deployed a containerized microservice application on **AWS EKS** (Kubernetes) with Amazon ECR image pipelines, Nginx ingress, Amazon RDS PostgreSQL, and ElastiCache Redis.
- **AI Question Synthesis Engine**: Integrated **Google Gemini 3.1 Flash Lite** (`google-genai` SDK) to generate structured, syllabus-aligned question papers in **English** and **Kannada** across 3 source material modes (`TOPIC_ONLY`, `PDF_ONLY`, `PDF_AND_TOPIC`) with strict topic isolation (`exact_topic`).
- **Multi-Agent Evaluation Pipeline**: Engineered a hybrid automated grading engine using exact-string matching for MCQs, rubric-guided evaluation for short answers, and multi-agent consensus scoring for long descriptive responses with partial credit support.
- **Enterprise Security & Analytics**: Implemented JWT authentication, role authorization (`recruiter` vs `candidate`), class-level exam isolation (Classes 1–12), IDOR protection, candidate answer-key sanitization, server-authoritative timers, and real-time performance analytics dashboards.
