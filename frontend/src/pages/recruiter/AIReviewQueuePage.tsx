import React, { useState } from 'react';
import { apiRequest } from '../../api/client';
import { ShieldAlert, CheckCircle2, Edit3, Loader2 } from 'lucide-react';

export const AIReviewQueuePage: React.FC = () => {
  const [submissionId, setSubmissionId] = useState('');
  const [overrideScore, setOverrideScore] = useState(85);
  const [reason, setReason] = useState('Reviewed candidate solution logic and confirmed partial credit for helper method implementation.');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmitOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');
    try {
      await apiRequest(`/reviews/${submissionId}`, {
        method: 'POST',
        body: JSON.stringify({
          override_score: Number(overrideScore),
          review_status: 'APPROVED',
          reason: reason
        })
      });
      setMessage(`✓ Recruiter score override successfully recorded for submission ${submissionId}.`);
    } catch (err: any) {
      setMessage(`Error: ${err.message || 'Failed recording review override.'}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-amber-400" /> Human-in-the-Loop AI Review Queue
        </h1>
        <p className="text-xs text-slate-400">Review low-confidence agent evaluations and apply authorized recruiter score overrides.</p>
      </div>

      {message && (
        <div className={`p-4 rounded-lg border text-sm ${message.startsWith('✓') ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmitOverride} className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-4">
        <div>
          <label className="block text-xs uppercase font-semibold text-slate-300 mb-1">Target Submission ID (UUID)</label>
          <input
            type="text"
            required
            value={submissionId}
            onChange={(e) => setSubmissionId(e.target.value)}
            placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
          />
        </div>

        <div>
          <label className="block text-xs uppercase font-semibold text-slate-300 mb-1">Authorized Override Score (0 - 100)</label>
          <input
            type="number"
            min={0}
            max={100}
            value={overrideScore}
            onChange={(e) => setOverrideScore(Number(e.target.value))}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
          />
        </div>

        <div>
          <label className="block text-xs uppercase font-semibold text-slate-300 mb-1">Review Reason & Audit Justification</label>
          <textarea
            required
            rows={3}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl transition-colors disabled:opacity-50"
          >
            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Edit3 className="w-4 h-4" />} Record Score Override
          </button>
        </div>
      </form>
    </div>
  );
};
