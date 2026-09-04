import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getAttemptByIdApi } from '../../api/attempts';
import { getQuestionsForExamApi } from '../../api/exams';
import { submitCodeApi } from '../../api/submissions';
import { saveDraftApi, sendTelemetryApi } from '../../api/telemetry';
import { ExamAttempt, Question } from '../../types/exam';
import { SubmissionResponse } from '../../types/submission';
import { MonacoCodeEditor } from '../../components/editor/MonacoCodeEditor';
import { ExamTimer } from '../../components/exam/ExamTimer';
import { ProctoringIndicator } from '../../components/proctoring/ProctoringIndicator';
import { LiveEvaluationProgress } from '../../components/evaluation/LiveEvaluationProgress';
import { useExamWebSocket } from '../../websocket/useExamWebSocket';
import { useSubmissionWebSocket } from '../../websocket/useSubmissionWebSocket';
import { Play, Save, AlertCircle, Loader2, FileCode, ArrowLeft, RefreshCw, CheckCircle2 } from 'lucide-react';

export const CandidateIDEPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<ExamAttempt | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number>(0);
  const [code, setCode] = useState<string>('# Write your Python solution here\ndef solve():\n    pass\n');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [lastSavedTime, setLastSavedTime] = useState<string>('');
  const [error, setError] = useState('');
  const [activeSubmissionId, setActiveSubmissionId] = useState<string | null>(null);

  const activeQuestion = questions[activeQuestionIndex] || null;

  // Real-time WebSockets
  const { connected: examWsConnected } = useExamWebSocket(attemptId);
  const { lastEvent: subEvent } = useSubmissionWebSocket(activeSubmissionId || undefined);

  const initIDE = async () => {
    if (!attemptId) return;
    setLoading(true);
    setError('');
    try {
      const att = await getAttemptByIdApi(attemptId);
      setAttempt(att);
      const qList = await getQuestionsForExamApi(att.exam_id);
      setQuestions(qList);
    } catch (err: any) {
      setError(err.message || 'Unable to load this exam attempt.');
    } finally {
      setLoading(false);
    }
  };

  // Load attempt & questions
  useEffect(() => {
    initIDE();
  }, [attemptId]);

  // Proctoring telemetry event listeners
  useEffect(() => {
    if (!attemptId) return;

    function handleBlur() {
      sendTelemetryApi(attemptId!, [{ event_type: 'FOCUS_LOST', duration_ms: 0 }]);
    }

    function handlePaste() {
      sendTelemetryApi(attemptId!, [{ event_type: 'PASTE_DETECTED', duration_ms: 0 }]);
    }

    window.addEventListener('blur', handleBlur);
    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('blur', handleBlur);
      window.removeEventListener('paste', handlePaste);
    };
  }, [attemptId]);

  // Auto-redirect on evaluation completion event
  useEffect(() => {
    if (subEvent && subEvent.event_type === 'EVALUATION_STAGE_CHANGED' && subEvent.progress === 100) {
      if (activeSubmissionId) {
        setTimeout(() => {
          navigate(`/candidate/submissions/${activeSubmissionId}`);
        }, 1500);
      }
    }
  }, [subEvent, activeSubmissionId, navigate]);

  // Save Draft
  const handleSaveDraft = async () => {
    if (!attemptId || !activeQuestion) return;
    setSavingDraft(true);
    try {
      await saveDraftApi(attemptId, activeQuestion.id, code);
      setLastSavedTime(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError('Draft save notice: ' + (err.message || 'Could not reach draft endpoint.'));
    } finally {
      setSavingDraft(false);
    }
  };

  // Submit Code
  const handleSubmitCode = async () => {
    if (!attemptId || !attempt || !activeQuestion) return;
    setSubmitting(true);
    setError('');
    try {
      const res: SubmissionResponse = await submitCodeApi({
        exam_id: attempt.exam_id,
        attempt_id: attempt.id,
        question_id: activeQuestion.id,
        language: 'python',
        code: code,
      });
      setActiveSubmissionId(res.submission_id);
    } catch (err: any) {
      setError(err.message || 'Code submission failed.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">Loading IDE session & proctoring environment...</p>
      </div>
    );
  }

  if (error || !attempt) {
    return (
      <div className="max-w-xl mx-auto my-12 p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center space-y-4 shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-400 flex items-center justify-center mx-auto border border-rose-500/20">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Unable to Load Exam Attempt</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          {error || 'The requested exam attempt could not be retrieved from the server.'}
        </p>
        <div className="flex items-center justify-center gap-3 pt-4 border-t border-slate-800">
          <button
            onClick={initIDE}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Try Again
          </button>
          <Link
            to="/candidate"
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all flex items-center gap-1.5"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Available Exams
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 font-sans">
      {/* Top Session Bar */}
      <div className="bg-slate-900 p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-emerald-400" />
            <h1 className="font-black text-white text-base">EduExam Assessment Workspace</h1>
          </div>
          <ProctoringIndicator connected={examWsConnected} />
        </div>

        <div className="flex items-center gap-4 text-xs">
          {lastSavedTime && (
            <span className="text-emerald-400 font-medium hidden sm:block">✓ Saved at {lastSavedTime}</span>
          )}
          {attempt && (
            <ExamTimer
              expiresAt={attempt.expires_at}
              onExpire={() => navigate('/candidate')}
            />
          )}
        </div>
      </div>

      {/* Main IDE Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0">
        {/* Left Column: Questions Sidebar & Description */}
        <div className="lg:col-span-4 bg-slate-900 p-5 rounded-2xl border border-slate-800 flex flex-col space-y-4 overflow-y-auto">
          {/* Question Navigation Tabs */}
          {questions.length > 0 && (
            <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800">
              {questions.map((q, idx) => (
                <button
                  key={q.id}
                  onClick={() => setActiveQuestionIndex(idx)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-black shrink-0 transition-all ${
                    activeQuestionIndex === idx
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                      : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'
                  }`}
                >
                  Q{idx + 1}
                </button>
              ))}
            </div>
          )}

          {/* Active Question Content */}
          {activeQuestion ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-white">{activeQuestion.title}</h2>
                <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-extrabold uppercase">
                  {activeQuestion.difficulty}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {activeQuestion.description}
              </p>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
                <p>• Time Limit: <span className="text-slate-200 font-bold">{activeQuestion.time_limit_seconds}s</span></p>
                <p>• Memory Limit: <span className="text-slate-200 font-bold">{activeQuestion.memory_limit_mb}MB</span></p>
                <p>• Max Score: <span className="text-emerald-400 font-bold">{activeQuestion.max_score} pts</span></p>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 space-y-3">
              <p className="text-xs">No questions configured for this exam attempt yet.</p>
              <Link
                to="/candidate"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 hover:underline"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Return to Available Exams
              </Link>
            </div>
          )}
        </div>

        {/* Right Column: Code Editor & Submission Controls */}
        <div className="lg:col-span-8 flex flex-col space-y-3 min-h-0">
          <div className="flex-1 min-h-[350px] rounded-2xl overflow-hidden border border-slate-800">
            <MonacoCodeEditor
              code={code}
              onChange={setCode}
              language="python"
            />
          </div>

          {/* Action Toolbar */}
          <div className="bg-slate-900 p-3 rounded-2xl border border-slate-800 flex items-center justify-between">
            <button
              onClick={handleSaveDraft}
              disabled={savingDraft || !activeQuestion}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all disabled:opacity-50"
            >
              {savingDraft ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />} Save Draft
            </button>

            <button
              onClick={handleSubmitCode}
              disabled={submitting || !activeQuestion}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white text-xs font-bold transition-all disabled:opacity-50 shadow-lg shadow-emerald-600/20"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />} Submit Solution
            </button>
          </div>

          {/* Real-time Submission Pipeline Progress overlay */}
          {activeSubmissionId && (
            <LiveEvaluationProgress
              status={subEvent?.payload?.stage || 'QUEUED'}
              progress={subEvent?.progress || 0}
            />
          )}
        </div>
      </div>
    </div>
  );
};
