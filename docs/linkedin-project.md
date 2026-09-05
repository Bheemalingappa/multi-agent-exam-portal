# LinkedIn Project Description

## Title: Multi-Agent Exam & Evaluation Portal (EduExam)

### Summary
Built and deployed **EduExam**, a cloud-native K-12 examination and evaluation platform on **AWS EKS**, combining **Google Gemini** for AI question paper generation and a backend **Multi-Agent Consensus Engine** for automated student answer evaluation.

### Key Engineering Highlights:
- **AI Question Synthesis**: Integrated Google Gemini 3.1 Flash Lite (`google-genai` SDK) to generate structured, syllabus-aligned question papers (MCQ, Short Answer, Long Answer) in **English** and **Kannada** across 3 source material modes (`TOPIC_ONLY`, `PDF_ONLY`, `PDF_AND_TOPIC`).
- **Multi-Agent Evaluation Pipeline**: Developed a hybrid automated grading engine using exact matching for MCQs, rubric-guided evaluation for short answers, and multi-agent consensus scoring for long descriptive responses with partial marking support.
- **Class-Level Security & Authorization**: Implemented role-based access control (RBAC), strict class-level exam isolation (Classes 1–12), IDOR protection, candidate answer-key sanitization, and server-authoritative timers.
- **Production Cloud Infrastructure**: Containerized application microservices using Docker, pushed to Amazon ECR, and deployed to **AWS EKS** backed by Amazon RDS PostgreSQL and Amazon ElastiCache Redis.
- **Real-Time Performance Analytics**: Built educator and student analytics dashboards providing score trends over time, subject proficiency tracking, question itemized difficulty metrics (`Easy`/`Medium`/`Hard`), and sortable student performance rosters.

**Tech Stack**: Python, FastAPI, React 18, TypeScript, Google Gemini API, PostgreSQL, Redis, Docker, Kubernetes (AWS EKS), AWS NLB, Tailwind CSS.
