import { apiRequest } from './client';
import { SubmissionResponse, SubmissionDetail } from '../types/submission';
import { AnalyticsSummary } from '../types/analytics';

export async function submitCodeApi(data: {
  exam_id?: string;
  attempt_id?: string;
  question_id?: string;
  language?: string;
  code: string;
  telemetry?: any;
}): Promise<SubmissionResponse> {
  return apiRequest<SubmissionResponse>('/submissions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSubmissionByIdApi(submissionId: string): Promise<SubmissionDetail> {
  return apiRequest<SubmissionDetail>(`/submissions/${submissionId}`);
}

export async function getAnalyticsDashboardApi(): Promise<{ analytics: AnalyticsSummary }> {
  return apiRequest<{ analytics: AnalyticsSummary }>('/submissions/analytics/dashboard');
}
