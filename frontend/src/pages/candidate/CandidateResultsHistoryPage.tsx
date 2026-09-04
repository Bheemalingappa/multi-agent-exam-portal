import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Award, ArrowLeft, CheckCircle2, BarChart2, Calendar, FileText, Search, Filter, ArrowUpRight } from 'lucide-react';

interface ExamResultHistoryItem {
  id: string;
  examTitle: string;
  className: string;
  subject: string;
  date: string;
  score: number;
  maxScore: number;
  percentage: number;
  status: 'FINALIZED' | 'EVALUATING';
  evaluationDetailsId: string;
}

const MOCK_RESULTS: ExamResultHistoryItem[] = [
  { id: 'res-1', examTitle: 'Python Master Assessment 33', className: 'Class 10', subject: 'Computer Science', date: '2026-09-02', score: 100, maxScore: 100, percentage: 100, status: 'FINALIZED', evaluationDetailsId: 'ba7fed5b-b913-4121-8382-570f0a149cad' },
  { id: 'res-2', examTitle: 'Production Python Baseline Assessment', className: 'Class 10', subject: 'Computer Science', date: '2026-09-01', score: 95, maxScore: 100, percentage: 95, status: 'FINALIZED', evaluationDetailsId: 'a7d82cf8-51b4-4579-837d-38f5d2cfd197' },
  { id: 'res-3', examTitle: 'Algebra & Quadratic Equations Test', className: 'Class 10', subject: 'Mathematics', date: '2026-08-28', score: 88, maxScore: 100, percentage: 88, status: 'FINALIZED', evaluationDetailsId: 'ba7fed5b-b913-4121-8382-570f0a149cad' },
  { id: 'res-4', examTitle: 'Chemical Reactions & Optics Quiz', className: 'Class 10', subject: 'Science', date: '2026-08-24', score: 76, maxScore: 100, percentage: 76, status: 'FINALIZED', evaluationDetailsId: 'a7d82cf8-51b4-4579-837d-38f5d2cfd197' },
];

export const CandidateResultsHistoryPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState('all');

  const filteredResults = MOCK_RESULTS.filter((r) => {
    const matchSearch = r.examTitle.toLowerCase().includes(searchTerm.toLowerCase()) || r.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchSubject = selectedSubjectFilter === 'all' || r.subject.toLowerCase().includes(selectedSubjectFilter.toLowerCase());
    return matchSearch && matchSubject;
  });

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
          </button>
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
            <Award className="w-8 h-8 text-emerald-400" /> Exam History & Performance Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Track your class assessments, subject proficiency scores, and multi-agent AI evaluation reports.
          </p>
        </div>
      </div>

      {/* Subject Performance Breakdown */}
      <div className="p-8 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <BarChart2 className="w-5 h-5 text-indigo-400" /> Subject Proficiency & Skill Mastery
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs text-slate-400 font-medium">Computer Science</span>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-emerald-400">92%</span>
              <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">Strong</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '92%' }} />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs text-slate-400 font-medium">Mathematics</span>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-indigo-400">82%</span>
              <span className="text-[10px] font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">Proficient</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: '82%' }} />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs text-slate-400 font-medium">English Literature</span>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-amber-400">88%</span>
              <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">Strong</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: '88%' }} />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs text-slate-400 font-medium">Science</span>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-cyan-400">74%</span>
              <span className="text-[10px] font-semibold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">Good</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: '74%' }} />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-xs text-slate-400 font-medium">General Knowledge</span>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-purple-400">95%</span>
              <span className="text-[10px] font-semibold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">Master</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '95%' }} />
            </div>
          </div>
        </div>
      </div>

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
          {['all', 'Computer Science', 'Mathematics', 'Science'].map((sub) => (
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

      {/* Exam Results Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Assessment Name</th>
                <th className="px-6 py-4">Class Track</th>
                <th className="px-6 py-4">Subject</th>
                <th className="px-6 py-4">Completion Date</th>
                <th className="px-6 py-4">Score</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Evaluation Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {filteredResults.map((item) => (
                <tr key={item.id} className="hover:bg-slate-850/60 transition-colors">
                  <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <span>{item.examTitle}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-950 border border-slate-800 text-slate-300">
                      {item.className}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-300">{item.subject}</td>
                  <td className="px-6 py-4 text-slate-400 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>{item.date}</span>
                  </td>
                  <td className="px-6 py-4 font-bold text-emerald-400 text-sm">
                    {item.score} / {item.maxScore} ({item.percentage}%)
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" /> {item.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/candidate/submissions/${item.evaluationDetailsId}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white border border-emerald-500/30 transition-colors"
                    >
                      <span>View Scorecard</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
