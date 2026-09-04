import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createExamApi } from '../../api/exams';
import { ArrowLeft, Plus, AlertCircle, Loader2, BookOpen, Settings, FileText, CheckCircle2, Sparkles } from 'lucide-react';

export const CreateExamPage: React.FC = () => {
  const navigate = useNavigate();

  const [step, setStep] = useState<number>(1);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [targetClass, setTargetClass] = useState<string>('Class 10');
  const [subject, setSubject] = useState<string>('Computer Science');
  const [difficulty, setDifficulty] = useState('intermediate');
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [maxScore, setMaxScore] = useState(100);
  const [maxAttempts, setMaxAttempts] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const fullTitle = title.startsWith(targetClass) ? title : `${targetClass} ${subject} — ${title}`;

    try {
      const newExam = await createExamApi({
        title: fullTitle,
        description: `[${targetClass} | ${subject}] ${description}`,
        difficulty,
        duration_minutes: Number(durationMinutes),
        max_score: Number(maxScore),
        max_attempts: Number(maxAttempts),
      });
      navigate(`/recruiter/exams/${newExam.id}/questions`);
    } catch (err: any) {
      setError(err.message || 'Failed creating new exam.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <button
        onClick={() => navigate('/recruiter')}
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Educator Dashboard
      </button>

      {/* Stepper Header */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${step === 1 ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-emerald-500/20 text-emerald-300'}`}>1</span>
          <span className="text-xs font-bold text-white hidden sm:inline">Basic Info</span>
        </div>
        <div className="h-0.5 w-12 bg-slate-800" />
        <div className="flex items-center gap-3">
          <span className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${step === 2 ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : step > 2 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-500'}`}>2</span>
          <span className="text-xs font-bold text-slate-300 hidden sm:inline">Settings</span>
        </div>
        <div className="h-0.5 w-12 bg-slate-800" />
        <div className="flex items-center gap-3">
          <span className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${step === 3 ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-slate-800 text-slate-500'}`}>3</span>
          <span className="text-xs font-bold text-slate-300 hidden sm:inline">Review & Create</span>
        </div>
      </div>

      <div className="bg-slate-900/90 p-8 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Class 1–12 Assessment Authoring</span>
          <h1 className="text-2xl font-black text-white tracking-tight mt-1">Create New EduExam Assessment</h1>
          <p className="text-xs text-slate-400 mt-1">Configure class track, duration, scoring, and questions for AI evaluation.</p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Target Class Track</label>
                  <select
                    value={targetClass}
                    onChange={(e) => setTargetClass(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    {Array.from({ length: 12 }, (_, i) => `Class ${i + 1}`).map((cls) => (
                      <option key={cls} value={cls}>{cls}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Subject Discipline</label>
                  <select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    <option value="Computer Science">Computer Science & Coding</option>
                    <option value="Mathematics">Mathematics</option>
                    <option value="Science">Science</option>
                    <option value="English">English Literature</option>
                    <option value="Social Studies">Social Studies</option>
                    <option value="General Knowledge">General Knowledge</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Assessment Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Python & Data Structures Board Prep Assessment"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Assessment Description</label>
                <textarea
                  required
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Comprehensive evaluation testing algorithmic problem solving, AST module bans, and multi-agent AI grading."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
                >
                  Next: Exam Settings →
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Difficulty Level</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Duration (Minutes)</label>
                  <input
                    type="number"
                    min={5}
                    max={300}
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Maximum Marks</label>
                  <input
                    type="number"
                    value={maxScore}
                    onChange={(e) => setMaxScore(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">Max Allowed Attempts</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={maxAttempts}
                    onChange={(e) => setMaxAttempts(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
              </div>

              <div className="pt-4 flex justify-between">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 text-sm"
                >
                  ← Back
                </button>
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-xl text-sm transition-colors"
                >
                  Next: Review & Create →
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-indigo-500/20 text-indigo-300 uppercase">
                    {targetClass} • {subject}
                  </span>
                  <span className="text-xs text-slate-400 font-semibold">{durationMinutes} mins • {maxScore} pts</span>
                </div>
                <h3 className="text-lg font-bold text-white">{title || 'Untitled Assessment'}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{description || 'No description provided.'}</p>
              </div>

              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center gap-3">
                <Sparkles className="w-5 h-5 shrink-0" />
                <span>Upon creation, you will immediately be directed to the Question Manager to add test cases and code solutions.</span>
              </div>

              <div className="pt-4 flex justify-between">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 text-sm"
                >
                  ← Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-6 py-3 rounded-xl text-sm transition-colors shadow-lg shadow-emerald-600/20 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  <span>Create Assessment & Configure Questions</span>
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};
