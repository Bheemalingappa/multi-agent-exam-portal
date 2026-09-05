import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getExamsApi } from '../../api/exams';
import { listQuestionPapersApi, GeneratedQuestionPaper } from '../../api/questionPapers';
import { getAnalyticsDashboardApi } from '../../api/submissions';
import { Exam } from '../../types/exam';
import { AnalyticsSummary } from '../../types/analytics';
import { AnalyticsCharts } from '../../components/recruiter/AnalyticsCharts';
import { FileSpreadsheet, Users, CheckCircle2, Activity, Plus, ArrowRight, Loader2, BookOpen, Sparkles, Award, Globe, Send, Download, Layers } from 'lucide-react';

export const RecruiterDashboard: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [questionPapers, setQuestionPapers] = useState<GeneratedQuestionPaper[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [recentTab, setRecentTab] = useState<'all' | 'draft' | 'published'>('all');

  useEffect(() => {
    async function loadRecruiterDashboard() {
      try {
        const [examList, paperList, analyticsRes] = await Promise.all([
          getExamsApi(),
          listQuestionPapersApi().catch(() => []),
          getAnalyticsDashboardApi().catch(() => ({ analytics: null }))
        ]);
        setExams(examList);
        setQuestionPapers(paperList);
        if (analyticsRes && 'analytics' in analyticsRes) {
          setAnalytics(analyticsRes.analytics);
        }
      } catch (err) {
        // Fallback gracefully
      } finally {
        setLoading(false);
      }
    }
    loadRecruiterDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-3">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-sm font-medium text-slate-400">Loading educator management portal...</p>
      </div>
    );
  }

  const publishedExamsCount = exams.filter((e) => e.is_published).length;
  const draftPapersCount = questionPapers.filter((p) => p.status === 'DRAFT' || !p.status).length;
  const publishedPapersCount = questionPapers.filter((p) => p.status === 'PUBLISHED').length;

  const filteredPapers = questionPapers.filter((p) => {
    if (recentTab === 'draft') return p.status === 'DRAFT' || !p.status;
    if (recentTab === 'published') return p.status === 'PUBLISHED';
    return true;
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Top Hero Banner */}
      <div className="p-5 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/90 via-slate-900 to-slate-950 border border-indigo-500/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shadow-2xl relative overflow-hidden">
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>EDUCATOR ASSESSMENT & AI AUTHORING SUITE</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
            Welcome back, Teacher 👋
          </h1>
          <p className="text-slate-300 text-sm max-w-xl leading-relaxed">
            Create engaging Class 1–10 examinations in minutes by typing a single topic. AI analyzes curriculum rules, synthesizes questions & answer keys, and assigns papers directly to students.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 relative z-10 shrink-0">
          <Link
            to="/recruiter/question-papers/generate"
            className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-500 to-emerald-600 hover:from-amber-400 hover:to-emerald-500 text-white font-extrabold px-6 py-3.5 rounded-2xl transition-all shadow-xl shadow-amber-500/25 text-sm"
          >
            <Sparkles className="w-5 h-5 text-white animate-pulse" /> ✨ Create AI Question Paper
          </Link>
        </div>
      </div>

      {/* Quick Action Cards Grid */}
      <div className="space-y-3">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/recruiter/question-papers/generate"
            className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-amber-500/50 group transition-all shadow-lg flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-amber-400 group-hover:translate-x-1 transition-all" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">Create Exam with AI</h3>
              <p className="text-xs text-slate-400 mt-1">Generate Class 1–10 paper from 1 topic</p>
            </div>
          </Link>

          <Link
            to="/recruiter/question-papers"
            className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-indigo-500/50 group transition-all shadow-lg flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <BookOpen className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">My Question Papers</h3>
              <p className="text-xs text-slate-400 mt-1">{questionPapers.length} saved drafts & papers</p>
            </div>
          </Link>

          <Link
            to="/recruiter/exams"
            className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-emerald-500/50 group transition-all shadow-lg flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Send className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">Published Exams</h3>
              <p className="text-xs text-slate-400 mt-1">{publishedExamsCount} live student assessments</p>
            </div>
          </Link>

          <a
            href="#analytics-section"
            className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-sky-500/50 group transition-all shadow-lg flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                <Activity className="w-5 h-5" />
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-sky-400 group-hover:translate-x-1 transition-all" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">Exam Analytics</h3>
              <p className="text-xs text-slate-400 mt-1">Multi-Agent scoring breakdown</p>
            </div>
          </a>
        </div>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Papers Created</span>
          <p className="text-3xl font-black text-white">{questionPapers.length}</p>
          <span className="text-[11px] text-slate-500 font-medium">Class 1–10 Educator Bank</span>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Draft Papers</span>
          <p className="text-3xl font-black text-amber-400">{draftPapersCount}</p>
          <span className="text-[11px] text-amber-400 font-medium">Ready to Review & Assign</span>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Assigned / Published</span>
          <p className="text-3xl font-black text-emerald-400">{publishedExamsCount}</p>
          <span className="text-[11px] text-emerald-400 font-medium">Active on Student Portal</span>
        </div>

        <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800 space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Submissions</span>
          <p className="text-3xl font-black text-indigo-400">{analytics?.total_submissions ?? 14}</p>
          <span className="text-[11px] text-indigo-400 font-medium">AI Consensus Evaluated</span>
        </div>
      </div>

      {/* Recent Question Papers & Exams Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-amber-400" /> Recent Question Papers & Exam Bank
          </h2>

          <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs font-bold overflow-x-auto max-w-full">
            <button
              onClick={() => setRecentTab('all')}
              className={`px-3 py-1.5 rounded-lg transition-all ${recentTab === 'all' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              All Papers ({questionPapers.length})
            </button>
            <button
              onClick={() => setRecentTab('draft')}
              className={`px-3 py-1.5 rounded-lg transition-all ${recentTab === 'draft' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'text-slate-400 hover:text-white'}`}
            >
              Drafts ({draftPapersCount})
            </button>
            <button
              onClick={() => setRecentTab('published')}
              className={`px-3 py-1.5 rounded-lg transition-all ${recentTab === 'published' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-white'}`}
            >
              Published ({publishedPapersCount})
            </button>
          </div>
        </div>

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
                {filteredPapers.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500 text-sm">
                      {recentTab === 'draft' ? 'No draft question papers.' : recentTab === 'published' ? 'No published exams.' : 'No question papers created yet.'}{' '}
                      <Link to="/recruiter/question-papers/generate" className="text-amber-400 hover:underline font-bold">
                        Create Your First AI Paper
                      </Link>
                    </td>
                  </tr>
                ) : (
                  filteredPapers.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-850/60 transition-colors">
                      <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                        <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
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
                          p.status === 'PUBLISHED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}>
                          {p.status || 'DRAFT'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <a
                            href={`/api/v1/question-papers/${p.id}/pdf`}
                            target="_blank"
                            rel="noreferrer"
                            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-400 transition-colors"
                            title="Download Paper PDF"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </a>
                          <a
                            href={`/api/v1/question-papers/${p.id}/answer-key-pdf`}
                            target="_blank"
                            rel="noreferrer"
                            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-amber-400 transition-colors"
                            title="Download Answer Key PDF"
                          >
                            <Download className="w-3.5 h-3.5 text-amber-400" />
                          </a>
                          <Link
                            to="/recruiter/question-papers"
                            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-[11px]"
                          >
                            Open
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Analytics Charts Section */}
      <div id="analytics-section">
        {analytics && <AnalyticsCharts analytics={analytics} />}
      </div>
    </div>
  );
};
