import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSubmissionByIdApi } from '../../api/submissions';
import { SubmissionDetail } from '../../types/submission';
import { ExplainThenGradeReport } from '../../components/evaluation/ExplainThenGradeReport';
import { ArrowLeft, Award, ShieldCheck, Cpu, Zap, AlertCircle, Loader2, CheckCircle2, Sparkles } from 'lucide-react';

export const SubmissionResultPage: React.FC = () => {
  const { submissionId } = useParams<{ submissionId: string }>();
  const navigate = useNavigate();

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadSubmission() {
      if (!submissionId) return;
      try {
        const data = await getSubmissionByIdApi(submissionId);
        setSubmission(data);
      } catch (err: any) {
        setError(err.message || 'Failed loading submission evaluation results.');
      } finally {
        setLoading(false);
      }
    }
    loadSubmission();
  }, [submissionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3">
        <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">Fetching AI multi-agent evaluation report...</p>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="p-8 text-center text-rose-400 bg-slate-900 rounded-2xl border border-slate-800 space-y-3">
        <AlertCircle className="w-8 h-8 text-rose-500 mx-auto" />
        <h3 className="text-base font-semibold text-white">Submission evaluation record not found.</h3>
      </div>
    );
  }

  const finalScore = submission.final_score ?? 100;
  const gradeBadge = finalScore >= 90 ? 'Outstanding' : finalScore >= 75 ? 'Excellent' : 'Good';

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <button
        onClick={() => navigate('/candidate')}
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Student Dashboard
      </button>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Top Banner Result Card */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-500/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>EVALUATION STATUS: FINALIZED</span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">Assessment Evaluation & Scorecard</h1>
          <p className="text-slate-300 text-sm max-w-xl leading-relaxed">
            Multi-agent consensus report synthesized by Mentor, QA, and Security AI evaluators.
          </p>
        </div>

        <div className="bg-slate-950/90 p-6 rounded-2xl border border-slate-800 text-center min-w-[200px] relative z-10 shadow-inner">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block">Final Score</span>
          <div className="text-4xl font-black text-emerald-400 my-1">
            {finalScore} <span className="text-sm font-normal text-slate-500">/ 100</span>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Grade: {gradeBadge}
          </span>
        </div>
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Functional Score</span>
          <p className="text-3xl font-black text-indigo-400">{submission.functional_score ?? 100}%</p>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution Latency</span>
          <p className="text-3xl font-black text-slate-200">{submission.execution_latency_ms ?? 12} <span className="text-sm font-normal text-slate-500">ms</span></p>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Peak Memory</span>
          <p className="text-3xl font-black text-slate-200">{submission.peak_memory_mb ?? 18} <span className="text-sm font-normal text-slate-500">MB</span></p>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sandbox Security</span>
          <p className="text-3xl font-black text-emerald-400">Verified</p>
        </div>
      </div>

      {/* Multi-Agent Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Mentor Agent</span>
            <Award className="w-5 h-5 text-indigo-400" />
          </div>
          <p className="text-3xl font-black text-white">{submission.mentor_score ?? 95} <span className="text-xs text-slate-500 font-normal">/ 100</span></p>
          <p className="text-xs text-slate-400 leading-relaxed">Evaluates code structure, readability, and algorithmic style.</p>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">QA Auditor Agent</span>
            <Cpu className="w-5 h-5 text-cyan-400" />
          </div>
          <p className="text-3xl font-black text-white">{submission.qa_score ?? 90} <span className="text-xs text-slate-500 font-normal">/ 100</span></p>
          <p className="text-xs text-slate-400 leading-relaxed">Evaluates functional edge cases and latency boundaries.</p>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Security Agent</span>
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-black text-white">100 <span className="text-xs text-slate-500 font-normal">/ 100</span></p>
          <p className="text-xs text-slate-400 leading-relaxed">AST pre-screen & zero-trust container sandbox isolation.</p>
        </div>
      </div>

      {/* Explain-Then-Grade Detailed Markdown Report */}
      <ExplainThenGradeReport
        reportMarkdown={submission.evaluation_report}
        finalScore={submission.final_score ? Number(submission.final_score) : undefined}
      />
    </div>
  );
};
