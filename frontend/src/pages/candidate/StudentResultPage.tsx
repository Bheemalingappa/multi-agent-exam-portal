import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAttemptResultApi } from '../../api/attempts';
import { CheckCircle2, AlertCircle, Award, Percent, BookOpen, Clock, ArrowLeft, Loader2, FileCheck } from 'lucide-react';

export const StudentResultPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (attemptId) {
      fetchResult();
    }
  }, [attemptId]);

  const fetchResult = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAttemptResultApi(attemptId!);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load evaluation result.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
        <div className="flex items-center gap-3 text-emerald-400">
          <Loader2 className="w-8 h-8 animate-spin" />
          <span className="text-sm font-semibold">Loading Exam Evaluation Results...</span>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-8 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 text-center space-y-4 shadow-xl">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
          <h2 className="text-lg font-bold">Result Unavailable</h2>
          <p className="text-xs text-slate-400">{error || 'Evaluation result not found.'}</p>
          <Link to="/candidate" className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold rounded-xl transition-all">
            <ArrowLeft className="w-4 h-4" /> Back to Candidate Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const getGradeBadgeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    if (grade.startsWith('B')) return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    if (grade.startsWith('C')) return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
    return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10 space-y-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Link to="/candidate" className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-all">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Evaluation Completed
          </span>
        </div>

        {/* Hero Score Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-10">
            <Award className="w-48 h-48 text-emerald-400" />
          </div>

          <div className="relative z-10 space-y-6">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">
                <span>Class {result.class_level || 10}</span> • <span>{result.subject || 'General'}</span>
              </div>
              <h1 className="text-2xl lg:text-3xl font-extrabold text-white">{result.title}</h1>
            </div>

            {/* Score Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-800">
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 space-y-1">
                <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                  <FileCheck className="w-3.5 h-3.5 text-blue-400" /> Score
                </span>
                <p className="text-2xl font-black text-white">
                  {result.total_score} <span className="text-xs text-slate-400 font-normal">/ {result.maximum_score}</span>
                </p>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 space-y-1">
                <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                  <Percent className="w-3.5 h-3.5 text-emerald-400" /> Percentage
                </span>
                <p className="text-2xl font-black text-emerald-400">
                  {result.percentage}%
                </p>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 space-y-1">
                <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                  <Award className="w-3.5 h-3.5 text-amber-400" /> Grade
                </span>
                <div>
                  <span className={`px-3 py-0.5 border rounded-lg text-lg font-black ${getGradeBadgeColor(result.grade)}`}>
                    {result.grade}
                  </span>
                </div>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 space-y-1">
                <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-400" /> Questions
                </span>
                <p className="text-2xl font-black text-white">
                  {result.answered_questions} <span className="text-xs text-slate-400 font-normal">/ {result.total_questions}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Question Summary List */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-emerald-400" /> Question Breakdown
          </h2>

          <div className="space-y-3">
            {(result.question_summary || []).map((q: any, idx: number) => (
              <div key={q.question_id || idx} className="bg-slate-900 border border-slate-800/80 rounded-2xl p-5 space-y-3 shadow-sm">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md">
                        Q{q.number || idx + 1}
                      </span>
                      <span className="text-xs font-semibold text-slate-400 uppercase">
                        {q.question_type}
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-200">{q.question}</p>
                  </div>

                  <div className="text-right whitespace-nowrap">
                    <span className="text-sm font-bold text-white">
                      {q.awarded_marks} / {q.maximum_marks}
                    </span>
                    <div className="mt-1">
                      {q.correctness === 'CORRECT' && (
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold rounded-full">
                          Correct
                        </span>
                      )}
                      {q.correctness === 'PARTIAL' && (
                        <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-bold rounded-full">
                          Partial Credit
                        </span>
                      )}
                      {q.correctness === 'INCORRECT' && (
                        <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-bold rounded-full">
                          Incorrect
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {q.user_answer && (
                  <div className="p-3 bg-slate-950 rounded-xl border border-slate-800/60 text-xs text-slate-300">
                    <span className="text-[10px] font-bold text-slate-500 block uppercase mb-0.5">Your Response:</span>
                    <p className="font-mono text-slate-200">{q.user_answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
