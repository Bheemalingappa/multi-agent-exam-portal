export interface AnalyticsSummary {
  total_submissions: number;
  completed_submissions: number;
  failed_submissions?: number;
  pass_rate_percentage?: number;
  average_final_score: number;
  average_functional_score?: number;
  average_execution_latency_ms: number;
  average_peak_memory_mb?: number;
  average_anomaly_score?: number;
  flagged_proctoring_anomalies?: number;
}
