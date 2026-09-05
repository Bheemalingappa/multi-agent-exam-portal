import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getAttemptByIdApi, getAttemptQuestionsApi, autosaveAnswersApi, submitAttemptApi } from '../../api/attempts';
import { sendTelemetryApi } from '../../api/telemetry';
import { ExamAttempt } from '../../types/exam';
import { ExamTimer } from '../../components/exam/ExamTimer';
import { ProctoringIndicator } from '../../components/proctoring/ProctoringIndicator';
import { useExamWebSocket } from '../../websocket/useExamWebSocket';
import { Save, AlertCircle, Loader2, FileText, ArrowLeft, RefreshCw, CheckCircle2, Send, HelpCircle } from 'lucide-react';

export const CandidateIDEPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState<ExamAttempt | null>(null);
  const [examMeta, setExamMeta] = useState<any | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [savingStatus, setSavingStatus] = useState<'saved' | 'saving' | 'error'>('saved');
  const [lastSavedTime, setLastSavedTime] = useState<string>('');
  const [error, setError] = useState('');
  const [showSubmitConfirmModal, setShowSubmitConfirmModal] = useState(false);

  const activeQuestion = questions[activeQuestionIndex] || null;

  // Real-time WebSockets
  const { connected: examWsConnected } = useExamWebSocket(attemptId);

  const initExamSession = async () => {
    if (!attemptId) return;
    setLoading(true);
    setError('');
    try {
      const att = await getAttemptByIdApi(attemptId);
      setAttempt(att);
      setAnswers(att.answers || {});

      const qData = await getAttemptQuestionsApi(attemptId);
      setExamMeta(qData);
      setQuestions(qData.questions || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Unable to load this exam attempt.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initExamSession();
  }, [attemptId]);

  // Telemetry listeners
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

  // Handle Answer Selection / Input Change
  const handleAnswerChange = async (qKey: string, val: any) => {
    if (attempt?.status === 'SUBMITTED' || attempt?.status === 'COMPLETED' || attempt?.status === 'EXPIRED') return;
    
    const updatedAnswers = { ...answers, [qKey]: val };
    setAnswers(updatedAnswers);
    setSavingStatus('saving');

    try {
      await autosaveAnswersApi(attemptId!, { [qKey]: val });
      setSavingStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString());
    } catch (err: any) {
      setSavingStatus('error');
    }
  };

  // Submit Exam Attempt
  const handleFinalSubmit = async () => {
    if (!attemptId) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await submitAttemptApi(attemptId);
      setAttempt(res);
      setShowSubmitConfirmModal(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Exam submission failed.');
      setShowSubmitConfirmModal(false);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-3">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">Loading secure examination workspace...</p>
      </div>
    );
  }

  if (error && !attempt) {
    return (
      <div className="max-w-xl mx-auto my-12 p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center space-y-4 shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-400 flex items-center justify-center mx-auto border border-rose-500/20">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Unable to Load Exam Attempt</h2>
        <p className="text-xs text-slate-400 leading-relaxed">{error}</p>
        <div className="flex items-center justify-center gap-3 pt-4 border-t border-slate-800">
          <button
            onClick={initExamSession}
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

  const isSubmitted = attempt?.status === 'SUBMITTED' || attempt?.status === 'COMPLETED' || attempt?.status === 'EXPIRED';

  return (
    <div className="min-h-[calc(100vh-100px)] flex flex-col space-y-4 font-sans max-w-7xl mx-auto px-4 py-4">
      {/* Top Header Bar */}
      <div className="bg-slate-900 p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-400" />
            <div>
              <h1 className="font-black text-white text-base leading-tight">
                {examMeta?.title || 'Examination Workspace'}
              </h1>
              <p className="text-xs text-slate-400">
                Class {examMeta?.class_level || attempt?.exam_id} • {examMeta?.subject} ({examMeta?.language})
              </p>
            </div>
          </div>
          <ProctoringIndicator connected={examWsConnected} />
        </div>

        <div className="flex items-center gap-4 text-xs">
          {savingStatus === 'saving' && (
            <span className="text-amber-400 font-medium flex items-center gap-1">
              <Loader2 className="w-3 h-3 animate-spin" /> Saving...
            </span>
          )}
          {savingStatus === 'saved' && (
            <span className="text-emerald-400 font-medium hidden sm:flex items-center gap-1">
              ✓ Saved {lastSavedTime && `at ${lastSavedTime}`}
            </span>
          )}
          
          {attempt && !isSubmitted && (
            <ExamTimer
              expiresAt={attempt.expires_at}
              onExpire={initExamSession}
            />
          )}

          {isSubmitted && (
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-bold uppercase text-xs border border-emerald-500/30 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> {attempt.status}
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        {/* Left Column: Question Palette & Navigation */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Question Palette</h2>
              <span className="text-xs text-slate-400 font-semibold">
                {Object.keys(answers).length} / {questions.length} Answered
              </span>
            </div>

            {/* Grid Palette Buttons */}
            <div className="grid grid-cols-5 gap-2 max-h-[300px] overflow-y-auto pr-1">
              {questions.map((q, idx) => {
                const qKey = q.id || `q_${idx + 1}`;
                const numKey = String(q.number || idx + 1);
                const isAnswered = Boolean(answers[qKey] || answers[numKey]);
                const isActive = activeQuestionIndex === idx;

                return (
                  <button
                    key={qKey}
                    onClick={() => setActiveQuestionIndex(idx)}
                    className={`h-11 rounded-xl font-bold text-xs flex flex-col items-center justify-center transition-all ${
                      isActive
                        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 ring-2 ring-emerald-400'
                        : isAnswered
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-700/60'
                        : 'bg-slate-950 text-slate-400 border border-slate-800 hover:border-slate-700 hover:text-white'
                    }`}
                  >
                    <span>Q{idx + 1}</span>
                    {isAnswered && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-0.5"></span>}
                  </button>
                );
              })}
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-around text-[11px] text-slate-400">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-md bg-emerald-950 border border-emerald-700"></span> Answered
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-md bg-slate-950 border border-slate-800"></span> Unanswered
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-md bg-emerald-500"></span> Active
              </div>
            </div>
          </div>

          {/* Submission Card */}
          <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-3 shadow-xl">
            <h3 className="text-sm font-bold text-white">Finish Examination</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Once submitted, your answers will be locked and sent for evaluation.
            </p>

            {!isSubmitted ? (
              <button
                onClick={() => setShowSubmitConfirmModal(true)}
                disabled={submitting}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" /> Submit Exam
              </button>
            ) : (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium text-center space-y-1">
                <p className="font-bold">✓ Exam Submitted Successfully</p>
                {attempt?.submitted_at && (
                  <p className="text-[11px] text-slate-400">
                    Submitted at {new Date(attempt.submitted_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Question Content & Input */}
        <div className="lg:col-span-8">
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 space-y-6 shadow-xl min-h-[500px] flex flex-col justify-between">
            {activeQuestion ? (
              <div className="space-y-6">
                {/* Question Header */}
                <div className="flex items-start justify-between border-b border-slate-800 pb-4 gap-4">
                  <div>
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                      Question {activeQuestion.number || activeQuestionIndex + 1} of {questions.length}
                    </span>
                    <h2 className="text-lg font-bold text-white mt-1">
                      {activeQuestion.question || activeQuestion.title || `Question ${activeQuestionIndex + 1}`}
                    </h2>
                  </div>
                  <span className="text-xs px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 font-bold shrink-0">
                    {activeQuestion.marks || activeQuestion.max_score || 10} Marks
                  </span>
                </div>

                {/* Question Options or Input Field */}
                {activeQuestion.question_type === 'MCQ' || (activeQuestion.options && activeQuestion.options.length > 0) ? (
                  <div className="space-y-3 pt-2">
                    <p className="text-xs font-semibold text-slate-400">Select the correct option:</p>
                    <div className="space-y-2.5">
                      {activeQuestion.options.map((opt: string, optIdx: number) => {
                        const optPrefix = String.fromCharCode(65 + optIdx); // A, B, C, D
                        const qKey = activeQuestion.id || `q_${activeQuestionIndex + 1}`;
                        const numKey = String(activeQuestion.number || activeQuestionIndex + 1);
                        const currentVal = answers[qKey] || answers[numKey];
                        const isSelected = currentVal === optPrefix || currentVal === opt;

                        return (
                          <button
                            key={optIdx}
                            onClick={() => handleAnswerChange(qKey, optPrefix)}
                            disabled={isSubmitted}
                            className={`w-full p-4 rounded-xl text-left text-xs font-medium transition-all flex items-center gap-3 border ${
                              isSelected
                                ? 'bg-emerald-500/20 border-emerald-500 text-white shadow-md'
                                : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-950'
                            } ${isSubmitted ? 'cursor-not-allowed opacity-80' : ''}`}
                          >
                            <span className={`w-7 h-7 rounded-lg font-extrabold text-xs flex items-center justify-center shrink-0 border ${
                              isSelected
                                ? 'bg-emerald-500 text-white border-emerald-400'
                                : 'bg-slate-900 text-slate-400 border-slate-700'
                            }`}>
                              {optPrefix}
                            </span>
                            <span className="leading-relaxed">{opt}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3 pt-2">
                    <p className="text-xs font-semibold text-slate-400">Type your answer below:</p>
                    <textarea
                      value={answers[activeQuestion.id || `q_${activeQuestionIndex + 1}`] || ''}
                      onChange={(e) => handleAnswerChange(activeQuestion.id || `q_${activeQuestionIndex + 1}`, e.target.value)}
                      disabled={isSubmitted}
                      rows={8}
                      placeholder="Write your detailed answer here..."
                      className={`w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 leading-relaxed resize-y ${
                        isSubmitted ? 'cursor-not-allowed opacity-80' : ''
                      }`}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center text-slate-400">
                No question selected.
              </div>
            )}

            {/* Navigation Footer */}
            <div className="pt-6 border-t border-slate-800 flex items-center justify-between">
              <button
                onClick={() => setActiveQuestionIndex((prev) => Math.max(0, prev - 1))}
                disabled={activeQuestionIndex === 0}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all disabled:opacity-40"
              >
                Previous Question
              </button>

              <button
                onClick={() => setActiveQuestionIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                disabled={activeQuestionIndex >= questions.length - 1}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all disabled:opacity-40"
              >
                Next Question
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Final Submit Confirmation Modal */}
      {showSubmitConfirmModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full space-y-4 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-3 text-amber-400">
              <HelpCircle className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Confirm Exam Submission</h3>
            </div>
            
            <p className="text-xs text-slate-300 leading-relaxed">
              You are about to submit your exam. You cannot change your answers after submission.
            </p>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
              <p>• Total Questions: <span className="font-bold text-white">{questions.length}</span></p>
              <p>• Answered Questions: <span className="font-bold text-emerald-400">{Object.keys(answers).length}</span></p>
              <p>• Unanswered Questions: <span className="font-bold text-amber-400">{Math.max(0, questions.length - Object.keys(answers).length)}</span></p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowSubmitConfirmModal(false)}
                disabled={submitting}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleFinalSubmit}
                disabled={submitting}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all flex items-center gap-2"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />} Confirm & Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
