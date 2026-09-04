import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiRequest } from '../../api/client';
import { Activity, ShieldAlert, Clock, User, CheckCircle2, Loader2 } from 'lucide-react';

interface CandidateLiveStatus {
  attempt_id: string;
  candidate_id: string;
  status: string;
  started_at: string;
  expires_at: string;
  total_score: number;
}

export const LiveMonitorPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const [candidates, setCandidates] = useState<CandidateLiveStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLiveCandidates() {
      if (!examId) return;
      try {
        const res: any = await apiRequest(`/live/exams/${examId}`);
        setCandidates(res.attempts || []);
      } catch {
        setCandidates([]);
      } finally {
        setLoading(false);
      }
    }

    loadLiveCandidates();
    const interval = setInterval(loadLiveCandidates, 5000);
    return () => clearInterval(interval);
  }, [examId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Activity className="w-6 h-6 text-emerald-400" /> Real-Time Candidate Proctoring Stream
          </h1>
          <p className="text-xs text-slate-400">Live evaluation status, countdown timers, and proctoring anomaly confidence signals.</p>
        </div>
      </div>

      <div className="bg-slate-850 rounded-xl border border-slate-700 overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900 text-xs font-semibold uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4">Attempt ID</th>
              <th className="px-6 py-4">Candidate ID</th>
              <th className="px-6 py-4">Attempt Status</th>
              <th className="px-6 py-4">Score</th>
              <th className="px-6 py-4">Started At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {candidates.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                  No active candidate sessions currently detected for this assessment.
                </td>
              </tr>
            ) : (
              candidates.map((cand) => (
                <tr key={cand.attempt_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-indigo-400">{cand.attempt_id.substring(0, 8)}...</td>
                  <td className="px-6 py-4 text-xs font-medium text-slate-300 flex items-center gap-2">
                    <User className="w-3.5 h-3.5 text-slate-500" /> {cand.candidate_id.substring(0, 8)}...
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {cand.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-bold text-white text-xs">{cand.total_score} pts</td>
                  <td className="px-6 py-4 text-xs text-slate-400">{new Date(cand.started_at).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
