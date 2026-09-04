import React from 'react';
import { SubmissionStatus } from '../../types/submission';
import { CheckCircle2, Clock, Loader2, AlertTriangle, ShieldCheck } from 'lucide-react';

interface LiveEvaluationProgressProps {
  status: SubmissionStatus;
  progress?: number;
  errorMessage?: string;
}

const STAGES: { key: SubmissionStatus; label: string; progressPct: number }[] = [
  { key: 'QUEUED', label: 'Ingestion Queued', progressPct: 0 },
  { key: 'STATIC_ANALYSIS', label: 'AST Static Security Scan', progressPct: 10 },
  { key: 'SANDBOX_RUNNING', label: 'Ephemeral Container Spin-Up', progressPct: 20 },
  { key: 'TEST_CASE_EXECUTION', label: 'Hidden Test Cases Verification', progressPct: 35 },
  { key: 'MCP_CONTEXT', label: 'MCP Code-Context Injection', progressPct: 45 },
  { key: 'ANOMALY_ANALYSIS', label: 'Behavioral Anomaly Oracle', progressPct: 55 },
  { key: 'SECURITY_ANALYSIS', label: 'Security Vulnerability Agent', progressPct: 80 },
  { key: 'A2A_CONSENSUS', label: 'A2A Dual Consensus Negotiation', progressPct: 90 },
  { key: 'ADAPTIVE_ANALYSIS', label: 'Adaptive Challenge Engine', progressPct: 95 },
  { key: 'FINALIZED', label: 'Evaluation Report Finalized', progressPct: 100 },
];

export const LiveEvaluationProgress: React.FC<LiveEvaluationProgressProps> = ({
  status,
  progress,
  errorMessage,
}) => {
  const isFailed = ['FAILED', 'TIMEOUT', 'SECURITY_BLOCKED'].includes(status);
  const currentProgress = progress !== undefined ? progress : getStageProgress(status);

  function getStageProgress(st: SubmissionStatus): number {
    const stage = STAGES.find((s) => s.key === st);
    return stage ? stage.progressPct : st === 'FINALIZED' || st === 'COMPLETED' ? 100 : 50;
  }

  return (
    <div className="bg-slate-850 p-6 rounded-xl border border-slate-700 shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-indigo-400" />
          <h3 className="text-lg font-semibold text-white">Live Multi-Agent Pipeline Status</h3>
        </div>
        <span className={`px-3 py-1 text-xs font-semibold rounded-full uppercase tracking-wider ${
          status === 'FINALIZED' || status === 'COMPLETED'
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
            : isFailed
            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
            : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 animate-pulse'
        }`}>
          {status}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-medium text-slate-400">
          <span>Overall Completion</span>
          <span>{currentProgress}%</span>
        </div>
        <div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden border border-slate-700">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              isFailed ? 'bg-rose-500' : 'bg-gradient-to-r from-indigo-500 to-emerald-400'
            }`}
            style={{ width: `${currentProgress}%` }}
          />
        </div>
      </div>

      {/* Error Callout */}
      {isFailed && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Pipeline Execution Terminated</p>
            <p className="text-rose-400 text-xs mt-1">{errorMessage || 'Evaluation encountered a runtime limit or static security violation.'}</p>
          </div>
        </div>
      )}

      {/* Pipeline Stages Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
        {STAGES.map((stg) => {
          const isDone = currentProgress > stg.progressPct || status === 'FINALIZED';
          const isCurrent = status === stg.key;

          return (
            <div
              key={stg.key}
              className={`flex items-center gap-3 p-3 rounded-lg border text-sm transition-all ${
                isDone
                  ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                  : isCurrent
                  ? 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200 font-medium'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin shrink-0" />
              ) : (
                <Clock className="w-4 h-4 text-slate-600 shrink-0" />
              )}
              <span className="truncate">{stg.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
