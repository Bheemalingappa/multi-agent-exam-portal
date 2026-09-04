import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getExamByIdApi } from '../../api/exams';
import { startAttemptApi } from '../../api/attempts';
import { Exam } from '../../types/exam';
import { Clock, Award, ShieldAlert, ArrowLeft, Play, Loader2, AlertCircle } from 'lucide-react';

export const ExamDetailPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  useEffect(() => {
    async function loadDetail() {
      if (!examId) return;
      try {
        const data = await getExamByIdApi(examId);
        setExam(data);
      } catch (err: any) {
        setError(err.message || 'Failed loading exam details.');
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [examId]);

  const handleStartAttempt = async () => {
    if (!examId) return;
    setStarting(true);
    setError('');
    try {
      const attempt = await startAttemptApi(examId);
      navigate(`/candidate/attempts/${attempt.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start exam attempt.');
      setShowConfirmModal(false);
    } finally {
      setStarting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="p-8 text-center text-rose-400 bg-slate-850 rounded-xl border border-slate-800">
        Exam assessment not found.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <button
        onClick={() => navigate('/candidate')}
        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Exams
      </button>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-850 p-8 rounded-2xl border border-slate-700 space-y-6">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 text-xs font-semibold uppercase rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {exam.difficulty}
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> {exam.duration_minutes} minutes
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">{exam.title}</h1>
          <p className="text-slate-300 text-sm leading-relaxed">{exam.description}</p>
        </div>

        {/* Assessment Rules */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-md font-semibold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" /> Assessment Rules & Proctoring
          </h3>
          <ul className="text-xs text-slate-300 space-y-2 list-disc pl-5 leading-relaxed">
            <li>The server countdown timer starts immediately once confirmed and cannot be paused.</li>
            <li>Code is executed in an ephemeral non-root Alpine container with 128MB RAM and 0.5 CPU limits.</li>
            <li>AST static analysis will reject prohibited module imports (e.g. `os`, `subprocess`, `ctypes`).</li>
            <li>Proctoring telemetry measures typing cadence, focus loss counts, and paste activity.</li>
          </ul>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <span className="text-sm text-slate-400">Allowed Attempts: <span className="font-semibold text-white">{exam.max_attempts}</span></span>
          <button
            onClick={() => setShowConfirmModal(true)}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-xl transition-colors shadow-lg shadow-indigo-600/30"
          >
            <Play className="w-4 h-4 fill-current" /> Start Assessment
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 p-6 rounded-2xl max-w-md w-full space-y-6 shadow-2xl">
            <h3 className="text-xl font-bold text-white">Start Exam Attempt?</h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              Once started, the {exam.duration_minutes}-minute server countdown timer will begin immediately.
            </p>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleStartAttempt}
                disabled={starting}
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors disabled:opacity-50"
              >
                {starting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Confirm & Start'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
