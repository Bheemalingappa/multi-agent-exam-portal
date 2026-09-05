# API Reference Documentation

## Overview
The **Multi-Agent Exam & Evaluation Portal** backend exposes RESTful APIs built with **FastAPI**. All protected endpoints require a JWT Bearer token in the `Authorization` header (`Authorization: Bearer <token>`).

Base URL (Production): `http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com`

---

## 1. System Health & Readiness

### `GET /api/v1/health`
- **Purpose**: System liveness check.
- **Authorization**: Public
- **Response**: `{"status": "healthy"}`

### `GET /api/v1/ready`
- **Purpose**: System readiness check (database & Redis connectivity).
- **Authorization**: Public
- **Response**: `{"status": "ready", "database": "connected", "redis": "connected"}`

---

## 2. Authentication Router (`/api/v1/auth`)

### `POST /api/v1/auth/register`
- **Purpose**: User registration.
- **Authorization**: Public
- **Payload**:
  ```json
  {
    "email": "teacher@school.com",
    "password": "Password123!",
    "role": "recruiter",
    "class_level": null
  }
  ```
- **Response**: `200 OK` `{"message": "User registered successfully."}`

### `POST /api/v1/auth/login`
- **Purpose**: User authentication and JWT issuance.
- **Authorization**: Public
- **Payload**: `{"email": "user@school.com", "password": "Password123!"}`
- **Response**: `200 OK` `{"access_token": "<JWT_TOKEN>", "token_type": "bearer", "user": {...}}`

---

## 3. Question Papers Router (`/api/v1/question-papers`)

### `POST /api/v1/question-papers/generate`
- **Purpose**: Generate AI questions via Google Gemini (SDK `google-genai`).
- **Authorization**: Teacher (`recruiter`)
- **Payload**:
  ```json
  {
    "class_level": 7,
    "subject": "Science",
    "topic": "Photosynthesis",
    "exact_topic": "Photosynthesis",
    "source_type": "TOPIC_ONLY",
    "language": "English",
    "difficulty": "medium",
    "duration_minutes": 30,
    "maximum_marks": 30.0,
    "sections": [
      {"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}
    ]
  }
  ```
- **Response**: `200 OK` Returns structured question paper object with `generation_provider = "GEMINI"`.

### `POST /api/v1/question-papers`
- **Purpose**: Save a question paper draft (with teacher edits).
- **Authorization**: Teacher (`recruiter`)
- **Response**: `201 Created` `{"message": "Question paper saved successfully.", "id": "<paper_id>"}`

### `POST /api/v1/question-papers/{paper_id}/publish`
- **Purpose**: Publish a draft paper and link an exam record.
- **Authorization**: Teacher (`recruiter` - Paper Owner)
- **Response**: `200 OK` `{"status": "PUBLISHED", "exam_id": "<exam_id>"}`

### `GET /api/v1/question-papers/{paper_id}/pdf`
- **Purpose**: Generate student printable Question Paper HTML/PDF.
- **Authorization**: Authenticated Users
- **Security Note**: Excludes correct answers, solutions, and rubrics.

### `GET /api/v1/question-papers/{paper_id}/answer-key-pdf`
- **Purpose**: Generate official Teacher Answer Key PDF.
- **Authorization**: Teacher (`recruiter` - Paper Owner)
- **Security Note**: Candidates attempting this endpoint receive `403 Forbidden`.

---

## 4. Exams & Assignment Router (`/api/v1/exams`)

### `POST /api/v1/exams/{exam_id}/assign`
- **Purpose**: Assign a published exam to a specific class.
- **Authorization**: Teacher (`recruiter` - Exam Owner)
- **Payload**:
  ```json
  {
    "class_level": 7,
    "start_at": "2026-09-05T00:00:00Z",
    "end_at": "2026-09-12T23:59:59Z"
  }
  ```
- **Response**: `200 OK` `{"id": "<assignment_id>", "class_level": 7, ...}`

### `GET /api/v1/exams`
- **Purpose**: List available active exams for the authenticated student.
- **Authorization**: Student (`candidate`)
- **Security Note**: Strictly filters exams by the student's assigned `class_level`.

### `POST /api/v1/exams/{exam_id}/attempts`
- **Purpose**: Start an exam attempt.
- **Authorization**: Student (`candidate` - Class Level Match)
- **Response**: `201 Created` Returns initialized attempt object with `remaining_seconds` derived from server timer.

---

## 5. Exam Attempts & Evaluation Router (`/api/v1/attempts`)

### `GET /api/v1/attempts/{attempt_id}`
- **Purpose**: Resume attempt or refresh workspace.
- **Authorization**: Student (`candidate` - Attempt Owner)
- **Security Note**: Sanitizes correct answers and solutions from response.

### `PUT /api/v1/attempts/{attempt_id}/answers`
- **Purpose**: Auto-save candidate answers.
- **Authorization**: Student (`candidate` - Attempt Owner)
- **Payload**: `{"answers": {"1": "Chlorophyll", "2": "Stomata allow gas exchange."}}`
- **Response**: `200 OK` `{"answers": {...}}`

### `POST /api/v1/attempts/{attempt_id}/submit`
- **Purpose**: Submit attempt and trigger Multi-Agent evaluation.
- **Authorization**: Student (`candidate` - Attempt Owner)
- **Response**: `200 OK` Updates attempt status to `SUBMITTED` and triggers asynchronous grading.

### `GET /api/v1/attempts/{attempt_id}/result`
- **Purpose**: Fetch evaluated attempt results.
- **Authorization**: Student (`candidate` - Attempt Owner) or Teacher (`recruiter` - Exam Owner)
- **Response**: `200 OK` Returns total score, percentage, grade, and itemized feedback. Candidate view omits internal agent prompts/metadata.

---

## 6. Analytics Router (`/api/v1/analytics`)

### `GET /api/v1/analytics/student/summary`
- **Purpose**: Student summary metrics (total attempted, completed, average percentage, latest grade).
- **Authorization**: Student (`candidate`)

### `GET /api/v1/analytics/student/performance`
- **Purpose**: Student performance score trend, subject proficiency, and grade distribution.
- **Authorization**: Student (`candidate`)

### `GET /api/v1/analytics/teacher/summary`
- **Purpose**: Teacher overview metrics (papers created, active assignments, total submissions, overall average, pass rate).
- **Authorization**: Teacher (`recruiter`)

### `GET /api/v1/analytics/exams/{exam_id}/performance`
- **Purpose**: Exam-level performance metrics, pass rate, score range, standard deviation, and grade distribution.
- **Authorization**: Teacher (`recruiter` - Exam Owner)

### `GET /api/v1/analytics/exams/{exam_id}/questions`
- **Purpose**: Itemized question difficulty, correct/incorrect/skipped counts, and accuracy percentage.
- **Authorization**: Teacher (`recruiter` - Exam Owner)

### `GET /api/v1/analytics/exams/{exam_id}/students`
- **Purpose**: Sortable student performance roster with performance flags (`High Performer`, `Average`, `Needs Improvement`).
- **Authorization**: Teacher (`recruiter` - Exam Owner)
