import { apiRequest } from './client';

export async function sendTelemetryApi(
  attemptId: string,
  events: Array<{ event_type: string; duration_ms?: number; metadata?: any }>
): Promise<any> {
  return apiRequest(`/attempts/${attemptId}/telemetry`, {
    method: 'POST',
    body: JSON.stringify({ events }),
  });
}

export async function saveDraftApi(attemptId: string, questionId: string, code: string): Promise<any> {
  return apiRequest(`/attempts/${attemptId}/drafts`, {
    method: 'POST',
    body: JSON.stringify({ question_id: questionId, code }),
  });
}
