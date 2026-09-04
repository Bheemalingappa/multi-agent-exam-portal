import React, { useState } from 'react';
import { apiRequest } from '../../api/client';
import { FileSearch, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

export const PlagiarismReviewPage: React.FC = () => {
  const [sub1, setSub1] = useState('');
  const [sub2, setSub2] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await apiRequest('/plagiarism/check', {
        method: 'POST',
        body: JSON.stringify({
          submission_id: sub1,
          compare_with_submission_id: sub2
        })
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Plagiarism similarity check failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileSearch className="w-6 h-6 text-rose-400" /> Advanced AST Plagiarism Inspector
        </h1>
        <p className="text-xs text-slate-400">Compare source code structural fingerprints and token Jaccard similarity across candidate submissions.</p>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleCheck} className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs uppercase text-slate-400 mb-1">Target Submission ID</label>
            <input
              type="text"
              required
              value={sub1}
              onChange={(e) => setSub1(e.target.value)}
              placeholder="Submission UUID A"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-white"
            />
          </div>
          <div>
            <label className="block text-xs uppercase text-slate-400 mb-1">Comparison Submission ID</label>
            <input
              type="text"
              required
              value={sub2}
              onChange={(e) => setSub2(e.target.value)}
              placeholder="Submission UUID B"
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-white"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Run Plagiarism Inspection'}
          </button>
        </div>
      </form>

      {result && (
        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-semibold text-slate-400">Risk Assessment</span>
            <span className={`px-3 py-1 text-xs font-bold rounded-full ${
              result.plagiarism_risk_level === 'HIGH' ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
            }`}>
              {result.plagiarism_risk_level} RISK
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400">AST Structural Similarity</span>
              <p className="text-2xl font-bold text-white">{result.ast_similarity_score}%</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400">Token Overlap Score</span>
              <p className="text-2xl font-bold text-white">{result.token_similarity_score}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
