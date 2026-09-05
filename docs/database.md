# Database Architecture & Entity Relationships

## 1. Relational Schema Overview

The application utilizes **Amazon RDS PostgreSQL** managed database instance with SQLAlchemy ORM schemas defined in `backend/app/database/models.py`.

```mermaid
erDiagram
    User ||--o{ QuestionPaper : "creates (Teacher)"
    User ||--o{ ExamAssignment : "assigns (Teacher)"
    User ||--o{ CandidateAttempt : "attempts (Student)"
    
    QuestionPaper ||--o{ Section : "contains"
    QuestionPaper ||--o{ Exam : "publishes into"
    Section ||--o{ Question : "contains"

    Exam ||--o{ ExamAssignment : "has assignments"
    ExamAssignment ||--o{ CandidateAttempt : "belongs to"
    CandidateAttempt ||--o{ CandidateAnswer : "contains"
    CandidateAttempt ||--o1 EvaluationResult : "evaluates into"

    User {
        uuid id PK
        string email
        string hashed_password
        string role "recruiter | candidate"
        integer class_level "1-12"
        datetime created_at
    }

    QuestionPaper {
        uuid id PK
        uuid created_by FK
        string title
        integer class_level
        string subject
        string topic
        string exact_topic
        string source_type "TOPIC_ONLY | PDF_ONLY | PDF_AND_TOPIC"
        string language "English | Kannada"
        string status "DRAFT | PUBLISHED"
        float maximum_marks
        integer duration_minutes
    }

    Section {
        uuid id PK
        uuid paper_id FK
        string name
        string question_type "MCQ | SHORT_ANSWER | LONG_ANSWER"
        integer num_questions
        float marks_per_question
    }

    Question {
        uuid id PK
        uuid section_id FK
        integer number
        text question_text
        json options
        text correct_answer
        text explanation
        float marks
    }

    Exam {
        uuid id PK
        uuid paper_id FK
        uuid created_by FK
        string title
        integer class_level
        string status "PUBLISHED | ASSIGNED | ARCHIVED"
    }

    ExamAssignment {
        uuid id PK
        uuid exam_id FK
        uuid assigned_by FK
        integer class_level
        datetime start_at
        datetime end_at
    }

    CandidateAttempt {
        uuid id PK
        uuid assignment_id FK
        uuid candidate_id FK
        uuid exam_id FK
        string status "STARTED | SUBMITTED | EVALUATED"
        datetime started_at
        datetime expires_at
        datetime submitted_at
    }

    CandidateAnswer {
        uuid id PK
        uuid attempt_id FK
        string question_number
        text answer_text
    }

    EvaluationResult {
        uuid id PK
        uuid attempt_id FK
        float total_score
        float maximum_score
        float percentage
        string grade "A | B | C | D | F"
        string status "COMPLETED"
        json itemized_scores
        datetime evaluated_at
    }
```

---

## 2. Table Specifications

### `users`
- **Primary Key**: `id` (UUID)
- **Attributes**: `email`, `hashed_password`, `role` (`recruiter` / `candidate`), `class_level` (1–12), `created_at`.
- **Indexes**: Unique index on `email`.

### `question_papers`
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `created_by` $\rightarrow$ `users(id)`
- **Attributes**: `title`, `class_level`, `subject`, `topic`, `exact_topic`, `source_type`, `language`, `status` (`DRAFT`, `PUBLISHED`), `maximum_marks`, `duration_minutes`.

### `exam_assignments`
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `exam_id` $\rightarrow$ `exams(id)`, `assigned_by` $\rightarrow$ `users(id)`
- **Attributes**: `class_level`, `start_at`, `end_at`.

### `candidate_attempts`
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `assignment_id` $\rightarrow$ `exam_assignments(id)`, `candidate_id` $\rightarrow$ `users(id)`, `exam_id` $\rightarrow$ `exams(id)`
- **Attributes**: `status` (`STARTED`, `SUBMITTED`, `EVALUATED`), `started_at`, `expires_at`, `submitted_at`.

### `evaluation_results`
- **Primary Key**: `id` (UUID)
- **Foreign Keys**: `attempt_id` $\rightarrow$ `candidate_attempts(id)` (1-to-1 relationship)
- **Attributes**: `total_score`, `maximum_score`, `percentage`, `grade`, `status`, `itemized_scores` (JSON), `evaluated_at`.
