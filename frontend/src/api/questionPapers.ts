import { apiRequest } from './client';

export interface SectionConfig {
  name: string;
  question_type: string;
  num_questions: number;
  marks_per_question: number;
}

export interface GeneratePaperParams {
  class_level: number;
  subject: string;
  topic?: string;
  exact_topic?: string;
  source_type?: 'TOPIC_ONLY' | 'PDF_ONLY' | 'PDF_AND_TOPIC';
  source_document_id?: string;
  source_context?: string;
  language?: string;
  difficulty: string;
  duration_minutes: number;
  maximum_marks: number;
  sections: SectionConfig[];
}

export interface AnalyzeTopicParams {
  class_level: number;
  subject: string;
  topic: string;
  language?: string;
}

export interface AnalyzeTopicResult {
  class_level: number;
  subject: string;
  language: string;
  topic: string;
  key_concepts: string[];
  question_areas: string[];
  learning_objectives: string[];
  recommended_difficulty: string;
  suggested_duration: number;
  suggested_marks: number;
}

export interface AnalyzePdfResult {
  document_id: string;
  filename: string;
  page_count: number;
  source_context: string;
  key_concepts: string[];
  suggested_topics: string[];
  summary: string;
}

export interface QuestionItem {
  number: number;
  question: string;
  options?: string[];
  correct_answer: string;
  marks: number;
  explanation: string;
  step_by_step_solution?: string;
}

export interface GeneratedSection {
  name: string;
  question_type: string;
  num_questions: number;
  marks_per_question: number;
  section_total_marks: number;
  questions: QuestionItem[];
}

export interface GeneratedQuestionPaper {
  id?: string;
  title: string;
  class_level: number;
  subject: string;
  topic: string;
  exact_topic?: string;
  source_type?: string;
  source_document_id?: string;
  source_context?: string;
  language?: string;
  difficulty: string;
  duration_minutes: number;
  maximum_marks: number;
  instructions: string;
  sections: GeneratedSection[];
  status?: string;
  generation_provider?: string;
  published_exam_id?: string;
  created_at?: string;
}

export async function generateQuestionPaperApi(params: GeneratePaperParams): Promise<GeneratedQuestionPaper> {
  return apiRequest<GeneratedQuestionPaper>('/question-papers/generate', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function analyzeTopicApi(params: AnalyzeTopicParams): Promise<AnalyzeTopicResult> {
  return apiRequest<AnalyzeTopicResult>('/question-papers/analyze-topic', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function analyzePdfApi(file: File): Promise<AnalyzePdfResult> {
  const formData = new FormData();
  formData.append('file', file);
  return apiRequest<AnalyzePdfResult>('/question-papers/analyze-pdf', {
    method: 'POST',
    body: formData,
  });
}

export async function saveQuestionPaperApi(data: GeneratedQuestionPaper): Promise<any> {
  return apiRequest<any>('/question-papers', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listQuestionPapersApi(): Promise<GeneratedQuestionPaper[]> {
  return apiRequest<GeneratedQuestionPaper[]>('/question-papers');
}

export async function getQuestionPaperDetailApi(id: string): Promise<GeneratedQuestionPaper> {
  return apiRequest<GeneratedQuestionPaper>(`/question-papers/${id}`);
}

export async function updateQuestionPaperApi(id: string, data: GeneratedQuestionPaper): Promise<any> {
  return apiRequest<any>(`/question-papers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function publishQuestionPaperApi(id: string, classLevel: number = 10): Promise<any> {
  return apiRequest<any>(`/question-papers/${id}/publish?class_level=${classLevel}`, {
    method: 'POST',
  });
}

export async function deleteQuestionPaperApi(id: string): Promise<any> {
  return apiRequest<any>(`/question-papers/${id}`, {
    method: 'DELETE',
  });
}
