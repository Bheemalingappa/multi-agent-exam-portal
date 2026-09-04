import { apiRequest } from './client';
import { Exam, Question, TestCase } from '../types/exam';

export async function getExamsApi(params?: { class_level?: number; subject?: string }): Promise<Exam[]> {
  const query = new URLSearchParams();
  if (params?.class_level !== undefined && params.class_level > 0) {
    query.set('class_level', params.class_level.toString());
  }
  if (params?.subject && params.subject.trim() !== '') {
    query.set('subject', params.subject.trim());
  }
  const queryString = query.toString() ? `?${query.toString()}` : '';
  return apiRequest<Exam[]>(`/exams${queryString}`);
}

export async function getExamByIdApi(examId: string): Promise<Exam> {
  return apiRequest<Exam>(`/exams/${examId}`);
}

export async function createExamApi(data: {
  title: string;
  description: string;
  class_level?: number;
  subject?: string;
  difficulty?: string;
  duration_minutes?: number;
  max_score?: number;
  max_attempts?: number;
}): Promise<Exam> {
  return apiRequest<Exam>('/exams', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function publishExamApi(examId: string): Promise<Exam> {
  return apiRequest<Exam>(`/exams/${examId}/publish`, {
    method: 'POST',
  });
}

export async function assignExamApi(examId: string, classLevel: number): Promise<{ id: string; exam_id: string; class_level: number; status: string }> {
  return apiRequest<{ id: string; exam_id: string; class_level: number; status: string }>(`/exams/${examId}/assign`, {
    method: 'POST',
    body: JSON.stringify({ class_level: classLevel }),
  });
}

export async function unpublishExamApi(examId: string): Promise<Exam> {
  return apiRequest<Exam>(`/exams/${examId}/unpublish`, {
    method: 'POST',
  });
}

export async function getQuestionsForExamApi(examId: string): Promise<Question[]> {
  return apiRequest<Question[]>(`/exams/${examId}/questions`);
}

export async function createQuestionApi(
  examId: string,
  data: {
    title: string;
    description: string;
    difficulty?: string;
    language?: string;
    time_limit_seconds?: number;
    memory_limit_mb?: number;
    max_score?: number;
  }
): Promise<Question> {
  return apiRequest<Question>(`/exams/${examId}/questions`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createTestCaseApi(
  questionId: string,
  data: {
    input_data: string;
    expected_output: string;
    is_hidden?: boolean;
    weight?: number;
    timeout_seconds?: number;
  }
): Promise<TestCase> {
  return apiRequest<TestCase>(`/questions/${questionId}/test-cases`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getTestCasesApi(questionId: string): Promise<TestCase[]> {
  return apiRequest<TestCase[]>(`/questions/${questionId}/test-cases`);
}
