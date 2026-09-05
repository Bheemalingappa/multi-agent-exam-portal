# Screenshot & Portfolio Demo Checklist

## Overview
This document outlines the recommended screenshots and visual assets to capture for presenting the **Multi-Agent Exam & Evaluation Portal** in portfolio presentations, GitHub README, or recruiter demonstrations.

---

## Recommended Screenshot Index

| # | Visual Target / Page Screen | Operational Context & Features to Highlight | Information to Redact / Mask |
| :--- | :--- | :--- | :--- |
| **1** | **User Login & Registration** | Role selector (`Teacher / Educator` vs `Student`), Class Level dropdown (1–12), JWT auth form. | Real passwords, JWT bearer tokens in network tab. |
| **2** | **Teacher Dashboard** | Created papers count, active assignments count, total submissions count, overall average score card. | Internal user UUIDs. |
| **3** | **AI Question Paper Generator** | Source mode tabs (`TOPIC_ONLY`, `PDF_ONLY`, `PDF_AND_TOPIC`), Subject, Topic input, Language dropdown (`English`, `Kannada`), Sections configuration table. | Gemini API key. |
| **4** | **PDF Source Analysis** | Drag-and-drop PDF upload modal, page count indicator, document context extraction summary. | Confidential personal data in uploaded sample PDFs. |
| **5** | **Generated Questions Review** | Structured generated questions (MCQ options, Short answer prompts, Long answer questions), provider indicator (`Provider: GEMINI`). | Raw prompt payload JSON. |
| **6** | **Question Draft Editor** | Inline question text editing, options modification, correct answer radio selector, explanation edit, save draft button. | N/A |
| **7** | **Publishing & Assignment Modal** | Exam publishing confirmation, Class 7 selection, start/end datetime pickers, active assignment toggle. | N/A |
| **8** | **Student Exam Catalog** | Class 7 candidate view showing available assigned exams, duration badge, maximum marks badge, "Start Exam" button. | N/A |
| **9** | **Student Exam Workspace** | Floating server-authoritative timer countdown, question navigator, MCQ option selectors, text area for short/long answers, "Autosaved" status badge. | N/A |
| **10** | **Submission Confirmation** | Exam submit modal, unanswered questions warning, final "Submit Exam" button. | N/A |
| **11** | **Student Evaluation Result** | Score card (e.g., `25.0 / 30.0`), Percentage (`83.33%`), Grade badge (`Grade A`), itemized question breakdown with partial credit display. | Private agent internal prompts/metadata. |
| **12** | **Student Performance History** | Score trend line chart over time, subject proficiency bars, recent exam attempt history table. | N/A |
| **13** | **Teacher Exam Analytics** | Total completed submissions, average score, high/low scores, pass percentage gauge, score standard deviation, grade distribution histogram. | N/A |
| **14** | **Itemized Question Analytics** | Question-wise accuracy bar chart, correct/incorrect/skipped counts, dynamic difficulty badges (`Easy`, `Medium`, `Hard`). | N/A |
| **15** | **Sortable Student Roster** | Student performance table with search filter, status (`EVALUATED`), score, percentage, grade, and performance flags (`High Performer`, `Average`, `Needs Improvement`). | Real student emails/names if sensitive. |
