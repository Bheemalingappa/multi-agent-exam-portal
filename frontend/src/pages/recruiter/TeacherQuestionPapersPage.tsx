import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listQuestionPapersApi, deleteQuestionPaperApi, publishQuestionPaperApi, GeneratedQuestionPaper } from '../../api/questionPapers';
import { assignExamApi } from '../../api/exams';
import { FileText, Plus, Download, Send, Trash2, Edit3, ArrowLeft, Loader2, Sparkles, CheckCircle2, Globe, X } from 'lucide-react';

export const TeacherQuestionPapersPage: React.FC = () => {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<GeneratedQuestionPaper[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [assigningPaper, setAssigningPaper] = useState<GeneratedQuestionPaper | null>(null);
  const [assigning, setAssigning] = useState<boolean>(false);

  const loadPapers = async () => {
    try {
      const data = await listQuestionPapersApi();
      setPapers(data);
    } catch (err: any) {
      setError(err.message || 'Failed loading teacher question papers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPapers();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this question paper draft?')) return;
    try {
      await deleteQuestionPaperApi(id);
      loadPapers();
    } catch (err: any) {
      alert(err.message || 'Failed to delete question paper.');
    }
  };

  const handlePublish = async (id: string) => {
    try {
      await publishQuestionPaperApi(id);
      alert('✨ Exam published successfully! Click "Assign to Class" to make it available to students.');
      loadPapers();
    } catch (err: any) {
      alert(err.message || 'Failed to publish exam.');
    }
  };

  const handleConfirmAssign = async () => {
    if (!assigningPaper) return;
    setAssigning(true);
    try {
      let examId = assigningPaper.published_exam_id;
      if (!examId) {
        const pubRes = await publishQuestionPaperApi(assigningPaper.id!);
        examId = pubRes.exam_id;
      }
      if (examId) {
        await assignExamApi(examId, assigningPaper.class_level);
        alert(`✨ Exam assigned successfully to Class ${assigningPaper.class_level}! Students of Class ${assigningPaper.class_level} can now view & attempt the exam.`);
        setAssigningPaper(null);
        loadPapers();
      }
    } catch (err: any) {
      alert(err.message || 'Failed assigning exam to class.');
    } finally {
      setAssigning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">Loading stored teacher question papers...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <button
            onClick={() => navigate('/recruiter')}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Educator Dashboard
          </button>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <FileText className="w-8 h-8 text-indigo-400" /> My Question Papers & Exam Bank
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your Class 1–10 Kannada & English question paper drafts, print PDFs, and assign exams to students.
          </p>
        </div>

        <Link
          to="/recruiter/question-papers/generate"
          className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold px-5 py-3 rounded-2xl transition-all shadow-xl shadow-emerald-600/25 text-sm"
        >
          <Sparkles className="w-4 h-4 text-amber-300" /> Generate New Paper
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="rounded-3xl border border-slate-800 bg-slate-900/90 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Title</th>
                <th className="px-6 py-4">Class</th>
                <th className="px-6 py-4">Subject</th>
                <th className="px-6 py-4">Language</th>
                <th className="px-6 py-4">Topic</th>
                <th className="px-6 py-4">Max Marks</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {papers.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500 text-sm">
                    No stored question papers found. Click <strong>Generate New Paper</strong> to create one.
                  </td>
                </tr>
              ) : (
                papers.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-850/60 transition-colors">
                    <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                      <FileText className="w-4 h-4 text-indigo-400" />
                      <span>{p.title}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-slate-950 border border-slate-800 text-slate-300">
                        Class {p.class_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-300">{p.subject}</td>
                    <td className="px-6 py-4 font-bold text-amber-300 flex items-center gap-1">
                      <Globe className="w-3 h-3 text-amber-400" /> {p.language || 'English'}
                    </td>
                    <td className="px-6 py-4 text-slate-400">{p.topic}</td>
                    <td className="px-6 py-4 font-bold text-emerald-400">{p.maximum_marks} pts</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase ${
                        p.status === 'ASSIGNED' ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30' : p.status === 'PUBLISHED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <a
                          href={`/api/v1/question-papers/${p.id}/pdf`}
                          target="_blank"
                          rel="noreferrer"
                          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-400 transition-colors"
                          title="Print Question Paper PDF"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>
                        <a
                          href={`/api/v1/question-papers/${p.id}/answer-key-pdf`}
                          target="_blank"
                          rel="noreferrer"
                          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 transition-colors"
                          title="Print Answer Key PDF"
                        >
                          <Download className="w-3.5 h-3.5 text-amber-400" />
                        </a>
                        {p.status !== 'PUBLISHED' && p.status !== 'ASSIGNED' && (
                          <button
                            onClick={() => handlePublish(p.id!)}
                            className="px-3 py-1.5 rounded-lg bg-indigo-600/40 hover:bg-indigo-600/60 text-indigo-300 font-semibold text-[11px] flex items-center gap-1 border border-indigo-500/30"
                          >
                            <Send className="w-3 h-3" /> Publish
                          </button>
                        )}
                        <button
                          onClick={() => setAssigningPaper(p)}
                          className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-[11px] flex items-center gap-1 shadow-md shadow-emerald-500/20"
                        >
                          <Send className="w-3 h-3" /> Assign Exam
                        </button>
                        <button
                          onClick={() => handleDelete(p.id!)}
                          className="p-2 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                          title="Delete Paper"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Assign Modal */}
      {assigningPaper && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Send className="w-5 h-5 text-emerald-400" /> ASSIGN EXAM TO CLASS
              </h3>
              <button onClick={() => setAssigningPaper(null)} className="text-slate-500 hover:text-white"><X className="w-4 h-4" /></button>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Target Class:</span>
                <span className="font-bold text-emerald-400">Class {assigningPaper.class_level}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Subject:</span>
                <span className="font-semibold text-white">{assigningPaper.subject}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Language:</span>
                <span className="font-semibold text-amber-300">{assigningPaper.language || 'English'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Topic:</span>
                <span className="font-semibold text-white">{assigningPaper.topic}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Maximum Marks:</span>
                <span className="font-bold text-emerald-400">{assigningPaper.maximum_marks} Marks</span>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Assigning will make this examination visible on the Student Portal for all <strong className="text-white">Class {assigningPaper.class_level}</strong> students. Students of other classes will not see this exam.
            </p>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setAssigningPaper(null)}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={assigning}
                onClick={handleConfirmAssign}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 flex items-center gap-1.5 disabled:opacity-50"
              >
                {assigning ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Send className="w-4 h-4" /> Confirm & Assign Exam</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

