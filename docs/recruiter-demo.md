# 2-Minute Recruiter Demonstration Script

## Overview
This script is designed for a fast-paced, high-impact 2-minute demonstration of **EduExam** during technical screening calls or recruiter presentations.

---

## Timestamped Script Outline

### `0:00 – 0:20` | Introduction & Overview
> "Hi! Today I'm demonstrating **EduExam**, an AI-powered K-12 examination and evaluation platform I built and deployed on **AWS EKS**. The platform combines **Google Gemini** for multi-lingual AI question paper generation and a backend **Multi-Agent Evaluation Engine** for automated grading. It’s fully containerized, backed by PostgreSQL and Redis, and features class-level security controls."

### `0:20 – 0:45` | Teacher Question Generation (AI & Languages)
> "In the Teacher Workspace, educators select grade levels from Class 1 to 12, subjects, and languages—including **English** and **Kannada**. Here, I’m selecting Class 7 Science and generating questions on *Photosynthesis* using Google Gemini. In seconds, Gemini synthesizes structured MCQ, Short Answer, and Long Answer questions with marking weightings and explanations."

### `0:45 – 1:05` | Editorial Review, Publish & Class Assignment
> "Teachers maintain full editorial authority. I can edit any question text, modify options, or save draft papers. Once satisfied, I click **Publish** and **Assign** this exam specifically to Class 7 students for a 7-day test window."

### `1:05 – 1:25` | Student Exam Workspace & Timer Security
> "Now switching to a Class 7 student account. The student sees their assigned exam in the catalog. When they click **Start Exam**, a server-authoritative timer begins counting down. As they answer, responses auto-save in the background. If the student refreshes the browser, their workspace resumes instantly without losing time or answers."

### `1:25 – 1:45` | Multi-Agent Evaluation & Security Demonstration
> "Upon submission, the Multi-Agent evaluation engine automatically grades the attempt—exact matching for MCQs, rubric partial credit for short answers, and multi-agent consensus for long descriptive responses. The student sees their score and grade, while correct answer keys and internal agent prompts are strictly hidden for security."

### `1:45 – 2:00` | Analytics & Conclusion
> "Finally, the teacher dashboard aggregates class performance metrics, pass rates, question itemized difficulty, and a sortable student roster with performance flags. If an unauthorized Class 8 student attempts to open this Class 7 exam, the system enforces a strict `403 Forbidden` response. Thank you!"
