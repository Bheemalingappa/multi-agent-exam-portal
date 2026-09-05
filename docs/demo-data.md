# Portfolio Demonstration Script & Demo Data Plan

## Overview
This document provides a step-by-step walkthrough script for showcasing the **Multi-Agent Exam & Evaluation Portal** to technical recruiters, engineering managers, or interviewers.

---

## 1. Demonstration Setup Parameters

- **Teacher Credentials**: `teacher_demo@eduexam.com` / `TeacherPass123!` (Role: `recruiter`)
- **Authorized Student (Class 7)**: `student_c7@eduexam.com` / `StudentPass123!` (Role: `candidate`, `class_level` = 7)
- **Unauthorized Student (Class 8)**: `student_c8@eduexam.com` / `StudentPass123!` (Role: `candidate`, `class_level` = 8)
- **Exam Subject**: Science
- **Language**: Kannada
- **Exact Topic**: ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ (Photosynthesis in Plants)
- **Class Level**: 7

---

## 2. Step-by-Step Demonstration Walkthrough Script

### Phase 1: AI Question Generation & Review (Teacher Workspace)
1. Log in as Teacher (`teacher_demo@eduexam.com`).
2. Navigate to **AI Question Paper Generator**.
3. Select Source Mode: **TOPIC_ONLY**.
4. Set parameters:
   - **Class**: Class 7
   - **Subject**: Science
   - **Language**: Kannada
   - **Topic**: `ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ`
   - **Difficulty**: Medium
   - **Sections**:
     - Section A (MCQ): 1 question (10 marks)
     - Section B (Short Answer): 1 question (10 marks)
     - Section C (Long Answer): 1 question (10 marks)
5. Click **Generate Questions via Gemini**.
6. Show structured question output generated in authentic Kannada text with `generation_provider = GEMINI`.
7. Demonstrate review & edit capability: modify option text or question wording.
8. Click **Save Draft** $\rightarrow$ Show saved status.
9. Click **Publish Exam** $\rightarrow$ Show linked exam creation.
10. Click **Assign Exam** $\rightarrow$ Assign to **Class 7** with active date window.

---

### Phase 2: Class Authorization Security Demo (Student Workspace)
1. Log in as Unauthorized Student (**Class 8**).
2. Show candidate exam catalog $\rightarrow$ Verify Class 7 exam is **NOT visible**.
3. Demonstrate direct URL attempt start $\rightarrow$ Show backend returns **`403 Forbidden`**.
4. Log out.

---

### Phase 3: Exam Taking, Autosave & Resume (Authorized Class 7 Student)
1. Log in as Authorized Student (**Class 7**).
2. Show candidate catalog $\rightarrow$ Class 7 Science Exam is visible.
3. Click **Start Exam** $\rightarrow$ Show floating server-authoritative timer countdown (30:00).
4. Answer questions:
   - Select MCQ option.
   - Enter short answer response.
   - Enter long answer explanation.
5. Show **Autosaved** indicator.
6. Refresh the browser page $\rightarrow$ Show that attempt state resumes instantly, answers are restored, and the timer continues seamlessly without resetting.
7. Click **Submit Exam** $\rightarrow$ Confirm submission modal.

---

### Phase 4: Multi-Agent Evaluation & Analytics Review
1. View Student Result Page:
   - Show Total Score (e.g., `25.0 / 30.0`), Percentage (`83.33%`), and Grade (`Grade A`).
   - Show question-by-question breakdown with partial credit.
   - Verify that correct answer key and internal agent prompts are strictly hidden from student view.
2. Log back in as Teacher:
   - Navigate to **Exam Analytics Dashboard**.
   - Show overall class performance score, pass rate, and grade distribution histogram.
   - Show question itemized difficulty table (`Easy`, `Medium`, `Hard`).
   - Show sortable student roster with performance flags (`High Performer`).
   - Open Official Teacher Answer Key PDF $\rightarrow$ Show complete marking scheme.
