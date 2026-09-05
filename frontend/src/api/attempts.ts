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

export async function getActiveAttemptForExamApi(examId: string): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/exams/${examId}/active-attempt`);
}

export async function getAttemptQuestionsApi(attemptId: string): Promise<any> {
  return apiRequest<any>(`/attempts/${attemptId}/questions`);
}

export async function autosaveAnswersApi(attemptId: string, answers: Record<string, any>): Promise<ExamAttempt> {
  return apiRequest<ExamAttempt>(`/attempts/${attemptId}/answers`, {
    method: 'PUT',
    body: JSON.stringify({ answers }),
  });
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

export async function getAttemptResultApi(attemptId: string): Promise<any> {
  return apiRequest<any>(`/attempts/${attemptId}/result`);
}

export async function retryEvaluationApi(attemptId: string, forceRecalculate = false): Promise<any> {
  return apiRequest<any>(`/attempts/${attemptId}/evaluate`, {
    method: 'POST',
    body: JSON.stringify({ force_recalculate: forceRecalculate }),
  });
}
