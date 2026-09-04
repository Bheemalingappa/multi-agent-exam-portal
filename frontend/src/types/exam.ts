export type Difficulty = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface Exam {
  id: string;
  title: string;
  description: string;
  class_level?: number;
  subject?: string;
  difficulty: Difficulty;
  duration_minutes: number;
  max_score: number;
  max_attempts: number;
  is_active: boolean;
  is_published: boolean;
  created_at: string;
}

export interface Question {
  id: string;
  exam_id: string;
  title: string;
  description: string;
  difficulty: Difficulty;
  language: string;
  time_limit_seconds: number;
  memory_limit_mb: number;
  max_score: number;
  question_order: number;
  is_active?: boolean;
}

export interface TestCase {
  id: string;
  question_id: string;
  test_case_order: number;
  input_data: string;
  expected_output: string;
  is_hidden: boolean;
  weight: number;
  timeout_seconds: number;
}

export type AttemptStatus = 'STARTED' | 'IN_PROGRESS' | 'SUBMITTED' | 'EVALUATING' | 'COMPLETED' | 'EXPIRED' | 'CANCELLED';

export interface ExamAttempt {
  id: string;
  candidate_id: string;
  exam_id: string;
  status: AttemptStatus;
  started_at: string;
  expires_at: string;
  remaining_seconds: number;
  submitted_at?: string;
  completed_at?: string;
  total_score: number;
  max_score: number;
}
