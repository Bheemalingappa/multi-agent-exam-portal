import { apiRequest } from './client';
import { ExamAttempt } from '../types/exam';

export async function startAttemptApi(examId: string): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/exams/${examId}/attempts`, {
    method: 'POST',
  });
}

export async function getAttemptByIdApi(attemptId: string): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/attempts/${attemptId}`);
}

export async function submitAttemptApi(attemptId: string): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/attempts/${attemptId}/submit`, {
    method: 'POST',
  });
}

export async function cancelAttemptApi(attemptId: string): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/attempts/${attemptId}/cancel`, {
    method: 'POST',
  });
}
