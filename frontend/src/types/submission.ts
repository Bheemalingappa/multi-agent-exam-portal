export type SubmissionStatus =
  | 'QUEUED'
  | 'STATIC_ANALYSIS'
  | 'SANDBOX_RUNNING'
  | 'TEST_CASE_EXECUTION'
  | 'EXECUTION_COMPLETE'
  | 'MCP_CONTEXT'
  | 'ANOMALY_ANALYSIS'
  | 'SECURITY_ANALYSIS'
  | 'MENTOR_ANALYSIS'
  | 'QA_ANALYSIS'
  | 'A2A_CONSENSUS'
  | 'ADAPTIVE_ANALYSIS'
  | 'COMPLETED'
  | 'FINALIZED'
  | 'FAILED'
  | 'TIMEOUT'
  | 'SECURITY_BLOCKED';

export interface SubmissionResponse {
  submission_id: string;
  celery_task_id?: string;
  status: SubmissionStatus;
  message: string;
}

export interface SubmissionDetail {
  submission_id: string;
  candidate_id: string;
  exam_id: string;
  attempt_id?: string;
  question_id?: string;
  sandbox_profile_id: string;
  language: string;
  source_code: string;
  status: SubmissionStatus;
  celery_task_id?: string;
  static_analysis_status?: string;
  security_risk_level?: string;
  functional_score?: number;
  execution_latency_ms?: number;
  peak_memory_mb?: number;
  exit_code?: number;
  stdout?: string;
  stderr?: string;
  anomaly_score?: number;
  paste_ratio?: number;
  focus_loss_count?: number;
  typing_anomaly_score?: number;
  mcp_context?: Record<string, any>;
  mcp_context_hash?: string;
  mentor_score?: number;
  qa_score?: number;
  consensus_score?: number;
  consensus_confidence?: number;
  a2a_consensus?: Record<string, any>;
  adaptive_challenge?: string;
  evaluation_report?: string;
  final_score?: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}
