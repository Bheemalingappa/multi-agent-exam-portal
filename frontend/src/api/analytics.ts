import { apiRequest } from './client';

export interface StudentSummaryResponse {
  total_attempted: number;
  completed_exams: number;
  average_percentage: number;
  highest_score: number;
  current_grade: string;
  latest_result: {
    evaluation_id: string;
    attempt_id: string;
    exam_id: string;
    exam_title: string;
    subject: string;
    score: number;
    max_score: number;
    percentage: number;
    grade: string;
    completed_at: string;
  } | null;
  recent_results: Array<{
    evaluation_id: string;
    attempt_id: string;
    exam_id: string;
    exam_title: string;
    subject: string;
    score: number;
    max_score: number;
    percentage: number;
    grade: string;
    date: string;
    status: string;
  }>;
}

export interface StudentPerformanceResponse {
  average_percentage: number;
  score_trend: Array<{
    date: string;
    exam_title: string;
    subject: string;
    score: number;
    percentage: number;
    grade: string;
  }>;
  subject_performance: Array<{
    subject: string;
    total_exams: number;
    average_percentage: number;
    highest_score: number;
    grade: string;
  }>;
  grade_distribution: Record<string, number>;
}

export interface TeacherSummaryResponse {
  total_question_papers: number;
  published_exams: number;
  active_assignments: number;
  total_submissions: number;
  average_score: number;
  highest_score: number;
  lowest_score: number;
  pass_percentage: number;
}

export interface ExamPerformanceResponse {
  exam_id: string;
  exam_title: string;
  subject: string;
  class_level: number;
  assigned_students: number;
  total_submissions: number;
  submission_percentage: number;
  average_score: number;
  highest_score: number;
  lowest_score: number;
  pass_rate: number;
  grade_distribution: Record<string, number>;
  topic_performance: Array<{
    topic: string;
    source_mode: string;
    attempts_count: number;
    average_score: number;
    mastery_percentage: number;
  }>;
}

export interface ExamQuestionAnalyticsResponse {
  exam_id: string;
  total_questions: number;
  questions: Array<{
    question_id: string;
    number: number;
    question: string;
    question_type: string;
    maximum_marks: number;
    attempts_count: number;
    correct_count: number;
    incorrect_count: number;
    skipped_count: number;
    accuracy_percentage: number;
    average_marks_awarded: number;
    is_difficult: boolean;
  }>;
}

export interface ExamStudentRosterResponse {
  exam_id: string;
  total_students: number;
  students: Array<{
    attempt_id: string;
    candidate_id: string;
    email: string;
    class_level: number;
    score: number;
    max_score: number;
    percentage: number;
    grade: string;
    submitted_at: string | null;
    evaluation_status: string;
    performance_flag: string;
  }>;
}

export async function getStudentSummaryApi(): Promise<StudentSummaryResponse> {
  return apiRequest<StudentSummaryResponse>('/analytics/student/summary');
}

export async function getStudentPerformanceApi(): Promise<StudentPerformanceResponse> {
  return apiRequest<StudentPerformanceResponse>('/analytics/student/performance');
}

export async function getTeacherSummaryApi(): Promise<TeacherSummaryResponse> {
  return apiRequest<TeacherSummaryResponse>('/analytics/teacher/summary');
}

export async function getExamPerformanceApi(examId: string): Promise<ExamPerformanceResponse> {
  return apiRequest<ExamPerformanceResponse>(`/analytics/exams/${examId}/performance`);
}

export async function getExamQuestionsAnalyticsApi(examId: string): Promise<ExamQuestionAnalyticsResponse> {
  return apiRequest<ExamQuestionAnalyticsResponse>(`/analytics/exams/${examId}/questions`);
}

export async function getExamStudentsRosterApi(examId: string): Promise<ExamStudentRosterResponse> {
  return apiRequest<ExamStudentRosterResponse>(`/analytics/exams/${examId}/students`);
}
