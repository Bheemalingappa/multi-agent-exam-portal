import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getExamByIdApi, getQuestionsForExamApi, createQuestionApi, createTestCaseApi, getTestCasesApi } from '../../api/exams';
import { Exam, Question, TestCase } from '../../types/exam';
import { ArrowLeft, Plus, FileCode, CheckCircle2, Shield, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';

export const ManageQuestionsPage: React.FC = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();

  const [exam, setExam] = useState<Exam | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Add Question State
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [qTitle, setQTitle] = useState('');
  const [qDesc, setQDesc] = useState('');
  const [qDiff, setQDiff] = useState('intermediate');
  const [qTimeLimit, setQTimeLimit] = useState(2);

  // Selected Question & Test Cases State
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [inputData, setInputData] = useState('');
  const [expectedOutput, setExpectedOutput] = useState('');
  const [isHidden, setIsHidden] = useState(true);

  const loadData = async () => {
    if (!examId) return;
    try {
      const e = await getExamByIdApi(examId);
      setExam(e);
      const qList = await getQuestionsForExamApi(examId);
      setQuestions(qList);
      if (qList.length > 0 && !selectedQuestion) {
        setSelectedQuestion(qList[0]);
        loadTestCases(qList[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed loading question bank.');
    } finally {
      setLoading(false);
    }
  };

  const loadTestCases = async (qId: string) => {
    try {
      const tcList = await getTestCasesApi(qId);
      setTestCases(tcList);
    } catch {
      setTestCases([]);
    }
  };

  useEffect(() => {
    loadData();
  }, [examId]);

  const handleCreateQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!examId) return;
    try {
      await createQuestionApi(examId, {
        title: qTitle,
        description: qDesc,
        difficulty: qDiff,
        time_limit_seconds: Number(qTimeLimit),
      });
      setShowAddQuestion(false);
      setQTitle('');
      setQDesc('');
      loadData();
    } catch (err: any) {
      setError(err.message || 'Failed adding question.');
    }
  };

  const handleAddTestCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedQuestion) return;
    try {
      await createTestCaseApi(selectedQuestion.id, {
        input_data: inputData,
        expected_output: expectedOutput,
        is_hidden: isHidden,
      });
      setInputData('');
      setExpectedOutput('');
      loadTestCases(selectedQuestion.id);
    } catch (err: any) {
      setError(err.message || 'Failed adding test case.');
    }
  };

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
        <button
          onClick={() => navigate('/recruiter/exams')}
          className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Exam Catalog
        </button>

        <button
          onClick={() => setShowAddQuestion(true)}
          className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-colors"
        >
          <Plus className="w-4 h-4" /> Add Question to Bank
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Questions Management Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Questions List */}
        <div className="lg:col-span-4 bg-slate-850 p-5 rounded-xl border border-slate-700 space-y-3">
          <h3 className="text-md font-bold text-white mb-2">Question Bank ({questions.length})</h3>

          {questions.map((q, idx) => (
            <div
              key={q.id}
              onClick={() => {
                setSelectedQuestion(q);
                loadTestCases(q.id);
              }}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                selectedQuestion?.id === q.id
                  ? 'bg-emerald-950/30 border-emerald-500/50 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-semibold uppercase mb-1">
                <span>Q{idx + 1}</span>
                <span className="text-emerald-400">{q.difficulty}</span>
              </div>
              <p className="font-bold text-sm truncate">{q.title}</p>
            </div>
          ))}
        </div>

        {/* Right Column: Selected Question Test Cases */}
        <div className="lg:col-span-8 bg-slate-850 p-6 rounded-xl border border-slate-700 space-y-6">
          {selectedQuestion ? (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedQuestion.title}</h2>
                <p className="text-xs text-slate-400 mt-1">{selectedQuestion.description}</p>
              </div>

              {/* Existing Test Cases List */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-slate-300">Configured Test Cases ({testCases.length})</h4>
                <div className="space-y-2">
                  {testCases.map((tc, idx) => (
                    <div key={tc.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {tc.is_hidden ? <EyeOff className="w-4 h-4 text-amber-400" /> : <Eye className="w-4 h-4 text-emerald-400" />}
                        <span className="font-semibold text-slate-200">Test Case #{idx + 1}</span>
                        <span className="text-slate-500">({tc.is_hidden ? 'HIDDEN' : 'VISIBLE'})</span>
                      </div>
                      <span className="text-slate-400">Weight: {tc.weight}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Add Test Case Form */}
              <form onSubmit={handleAddTestCase} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <h4 className="text-xs font-semibold uppercase text-emerald-400 tracking-wider">Add Hidden or Visible Test Case</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] uppercase text-slate-400 mb-1">Input Data (Piped via stdin)</label>
                    <input
                      type="text"
                      required
                      value={inputData}
                      onChange={(e) => setInputData(e.target.value)}
                      placeholder="e.g. 5\n10"
                      className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] uppercase text-slate-400 mb-1">Expected Output (SHA256 hashed)</label>
                    <input
                      type="text"
                      required
                      value={expectedOutput}
                      onChange={(e) => setExpectedOutput(e.target.value)}
                      placeholder="e.g. 15"
                      className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isHidden}
                      onChange={(e) => setIsHidden(e.target.checked)}
                      className="rounded bg-slate-950 border-slate-800 text-emerald-500"
                    />
                    Mark as Hidden Test Case (Protected from Candidate APIs)
                  </label>

                  <button
                    type="submit"
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-1.5 rounded-lg transition-colors"
                  >
                    Add Test Case
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 text-sm">Select a question to manage test cases.</div>
          )}
        </div>
      </div>

      {/* Add Question Modal */}
      {showAddQuestion && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 p-6 rounded-2xl max-w-lg w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Add New Question</h3>

            <form onSubmit={handleCreateQuestion} className="space-y-3">
              <div>
                <label className="block text-xs uppercase text-slate-400 mb-1">Question Title</label>
                <input
                  type="text"
                  required
                  value={qTitle}
                  onChange={(e) => setQTitle(e.target.value)}
                  placeholder="Two Sum Problem"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-white"
                />
              </div>

              <div>
                <label className="block text-xs uppercase text-slate-400 mb-1">Description & Requirements</label>
                <textarea
                  required
                  rows={4}
                  value={qDesc}
                  onChange={(e) => setQDesc(e.target.value)}
                  placeholder="Write a function solve() returning indices of two numbers summing to target."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-white"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddQuestion(false)}
                  className="text-xs text-slate-400 hover:text-white px-3 py-1.5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg"
                >
                  Save Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
