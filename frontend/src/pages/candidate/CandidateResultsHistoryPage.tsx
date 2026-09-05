import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Award, ArrowLeft, CheckCircle2, BarChart2, Calendar,
  FileText, Search, ArrowUpRight, Loader2, TrendingUp, Star
} from 'lucide-react';
import {
  getStudentSummaryApi, getStudentPerformanceApi,
  StudentSummaryResponse, StudentPerformanceResponse
} from '../../api/analytics';

export const CandidateResultsHistoryPage: React.FC = () => {
  const [summary, setSummary] = useState<StudentSummaryResponse | null>(null);
  const [performance, setPerformance] = useState<StudentPerformanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState('all');

  useEffect(() => {
    async function loadData() {
      try {
        const [sumRes, perfRes] = await Promise.all([
          getStudentSummaryApi(),
          getStudentPerformanceApi()
        ]);
        setSummary(sumRes);
        setPerformance(perfRes);
      } catch (err) {
        console.error('Failed to load student analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
        <p className="text-sm text-slate-400">Loading student results and performance analytics...</p>
      </div>
    );
  }

  const recentResults = summary?.recent_results || [];

  const filteredResults = recentResults.filter((r) => {
    const matchSearch = r.exam_title.toLowerCase().includes(searchTerm.toLowerCase()) || r.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchSubject = selectedSubjectFilter === 'all' || r.subject.toLowerCase().includes(selectedSubjectFilter.toLowerCase());
    return matchSearch && matchSubject;
  });

  const subjectsList = Array.from(new Set(recentResults.map(r => r.subject))).filter(Boolean);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
          </button>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <Award className="w-8 h-8 text-emerald-400" /> Student Results & Performance Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Track your class assessments, subject proficiency scores, and multi-agent evaluation reports.
          </p>
        </div>
      </div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Attempted</span>
          <div className="text-2xl font-black text-white">{summary?.total_attempted || 0}</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Completed</span>
          <div className="text-2xl font-black text-emerald-400">{summary?.completed_exams || 0}</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Average Score</span>
          <div className="text-2xl font-black text-indigo-400">{summary?.average_percentage || 0}%</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Highest Score</span>
          <div className="text-2xl font-black text-cyan-400">{summary?.highest_score || 0}%</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Overall Grade</span>
          <div className="text-2xl font-black text-amber-400">{summary?.current_grade || 'N/A'}</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Latest Exam</span>
          <div className="text-sm font-bold text-slate-200 truncate">
            {summary?.latest_result ? `${summary.latest_result.percentage}% (${summary.latest_result.grade})` : 'None'}
          </div>
        </div>
      </div>

      {/* Subject Performance Breakdown */}
      {performance && performance.subject_performance.length > 0 && (
        <div className="p-8 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-6">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-indigo-400" /> Subject Proficiency & Skill Mastery
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {performance.subject_performance.map((subj) => (
              <div key={subj.subject} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-400 font-medium">{subj.subject}</span>
                <div className="flex items-baseline justify-between">
                  <span className="text-2xl font-black text-emerald-400">{subj.average_percentage}%</span>
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Grade {subj.grade}
                  </span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, subj.average_percentage)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score Trend & Grade Distribution */}
      {performance && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" /> Score Trend Over Time
            </h3>

            {performance.score_trend.length === 0 ? (
              <p className="text-xs text-slate-500">No completed exams available yet.</p>
            ) : (
              <div className="space-y-3">
                {performance.score_trend.map((st, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <div>
                      <div className="font-bold text-white">{st.exam_title}</div>
                      <div className="text-slate-500">{st.date} • {st.subject}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-black text-emerald-400 text-sm">{st.percentage}%</div>
                      <div className="text-[10px] font-bold text-slate-400">Grade {st.grade}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Star className="w-5 h-5 text-amber-400" /> Grade Distribution
            </h3>

            <div className="space-y-2">
              {Object.entries(performance.grade_distribution).map(([g, count]) => (
                <div key={g} className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-950 border border-slate-850">
                  <span className="font-bold text-slate-300">Grade {g}</span>
                  <span className="font-black text-indigo-400">{count} {count === 1 ? 'Exam' : 'Exams'}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search exam name or subject..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 text-xs w-full md:w-auto overflow-x-auto">
          <button
            onClick={() => setSelectedSubjectFilter('all')}
            className={`px-3 py-1.5 rounded-xl font-medium capitalize transition-colors ${
              selectedSubjectFilter === 'all'
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            All Subjects
          </button>
          {subjectsList.map((sub) => (
            <button
              key={sub}
              onClick={() => setSelectedSubjectFilter(sub)}
              className={`px-3 py-1.5 rounded-xl font-medium capitalize transition-colors ${
                selectedSubjectFilter === sub
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {sub}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Exam Results Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Assessment Name</th>
                <th className="px-6 py-4">Subject</th>
                <th className="px-6 py-4">Completion Date</th>
                <th className="px-6 py-4">Score</th>
                <th className="px-6 py-4">Grade</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Scorecard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {filteredResults.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No exam results match your current search or filter criteria.
                  </td>
                </tr>
              ) : (
                filteredResults.map((item) => (
                  <tr key={item.evaluation_id} className="hover:bg-slate-850/60 transition-colors">
                    <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                      <FileText className="w-4 h-4 text-emerald-400" />
                      <span>{item.exam_title}</span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-300">{item.subject}</td>
                    <td className="px-6 py-4 text-slate-400 flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      <span>{item.date}</span>
                    </td>
                    <td className="px-6 py-4 font-bold text-emerald-400 text-sm">
                      {item.score} / {item.max_score} ({item.percentage}%)
                    </td>
                    <td className="px-6 py-4 font-bold text-amber-400">
                      {item.grade}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" /> {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        to={`/candidate/attempts/${item.attempt_id}/result`}
                        className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white border border-emerald-500/30 transition-colors"
                      >
                        <span>View Result</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
