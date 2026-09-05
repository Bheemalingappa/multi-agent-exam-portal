# Interview Elevator Pitch Options

## 1. 30-Second Elevator Pitch
> "I built and deployed **EduExam**, an AI-powered K-12 examination platform on **AWS EKS**. The system leverages **Google Gemini** for multi-lingual question paper generation across topic and PDF modes, and integrates a backend **Multi-Agent Evaluation Engine** for automated grading. Built with FastAPI, React, TypeScript, PostgreSQL, and Redis, it enforces class-level security and provides real-time performance analytics for educators."

---

## 2. 60-Second Elevator Pitch
> "EduExam is a cloud-native assessment platform designed to automate exam creation, delivery, and evaluation for K-12 institutions. On the creator side, educators select grade levels from Class 1 to 12 and topics to generate multi-lingual (`English` & `Kannada`) question papers via Google Gemini. Teachers can edit questions, publish exams, and assign active test windows to specific classes. 

> On the student side, the platform delivers exams through a secure workspace with a server-authoritative timer and background autosave. Submitted exams are graded automatically by a multi-agent evaluation pipeline supporting partial credit. I deployed the application microservices to AWS EKS using Docker and Kubernetes, backed by RDS PostgreSQL and ElastiCache Redis."

---

## 3. 2-Minute Technical Elevator Pitch
> "I developed **EduExam**, an end-to-end AI assessment platform deployed on **AWS EKS**. The engineering architecture addresses three core challenges in digital assessment: AI synthesis quality, examination security, and automated evaluation accuracy.

> For question synthesis, I integrated Google Gemini 3.1 Flash Lite using the `google-genai` SDK. The API generates structured JSON question papers across three source material modes—`TOPIC_ONLY`, `PDF_ONLY`, and `PDF_AND_TOPIC`. I implemented exact topic isolation (`exact_topic`) to focus question context while preventing verbatim copying from uploaded PDFs.

> For security, I implemented role-based JWT authentication, class-level authorization (blocking cross-grade access with `403 Forbidden`), IDOR protection on student attempts, candidate answer-key sanitization, and server-managed countdown timers ($\text{expires\_at} - \text{now}$).

> For evaluation, submitted exams route through a hybrid grading pipeline: exact matching for MCQs, rubric-guided partial scoring for short answers, and multi-agent consensus for long descriptive responses. The backend is built with FastAPI, PostgreSQL, and Redis, and frontend with React and TypeScript. The entire system is production-tested on AWS EKS."
