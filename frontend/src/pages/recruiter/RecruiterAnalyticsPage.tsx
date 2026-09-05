import React, { useEffect, useState } from 'react';
import {
  BarChart2, Loader2, BookOpen, CheckCircle, FileText,
  Users, Award, TrendingUp, HelpCircle, ArrowUpDown, AlertCircle
} from 'lucide-react';
import {
  getTeacherSummaryApi, getExamPerformanceApi,
  getExamQuestionsAnalyticsApi, getExamStudentsRosterApi,
  TeacherSummaryResponse, ExamPerformanceResponse,
  ExamQuestionAnalyticsResponse, ExamStudentRosterResponse
} from '../../api/analytics';
import { getExamsApi } from '../../api/exams';

interface ExamItem {
  id: string;
  title: string;
  subject: string;
  class_level: number;
}

export const RecruiterAnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<TeacherSummaryResponse | null>(null);
  const [exams, setExams] = useState<ExamItem[]>([]);
  const [selectedExamId, setSelectedExamId] = useState<string>('');

  const [examPerf, setExamPerf] = useState<ExamPerformanceResponse | null>(null);
  const [questionsAnalytics, setQuestionsAnalytics] = useState<ExamQuestionAnalyticsResponse | null>(null);
  const [studentsRoster, setStudentsRoster] = useState<ExamStudentRosterResponse | null>(null);

  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingExamDetails, setLoadingExamDetails] = useState(false);

  const [sortField, setSortField] = useState<'score' | 'percentage' | 'submitted_at' | 'grade'>('percentage');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    async function loadSummaryData() {
      try {
        const [sumRes, examsRes] = await Promise.all([
          getTeacherSummaryApi(),
          getExamsApi()
        ]);
        setSummary(sumRes);

        const examList = (examsRes || []).map((e: any) => ({
          id: e.id,
          title: e.title,
          subject: e.subject || 'General',
          class_level: e.class_level || 10
        }));
        setExams(examList);

        if (examList.length > 0) {
          setSelectedExamId(examList[0].id);
        }
      } catch (err) {
        console.error('Failed to load teacher summary analytics:', err);
      } finally {
        setLoadingSummary(false);
      }
    }
    loadSummaryData();
  }, []);

  useEffect(() => {
    if (!selectedExamId) return;

    async function loadExamDetails() {
      setLoadingExamDetails(true);
      try {
        const [perfRes, qRes, rosterRes] = await Promise.all([
          getExamPerformanceApi(selectedExamId),
          getExamQuestionsAnalyticsApi(selectedExamId),
          getExamStudentsRosterApi(selectedExamId)
        ]);
        setExamPerf(perfRes);
        setQuestionsAnalytics(qRes);
        setStudentsRoster(rosterRes);
      } catch (err) {
        console.error(`Failed to load details for exam ${selectedExamId}:`, err);
      } finally {
        setLoadingExamDetails(false);
      }
    }
    loadExamDetails();
  }, [selectedExamId]);

  if (loadingSummary) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
        <p className="text-sm text-slate-400">Loading teacher summary analytics...</p>
      </div>
    );
  }

  const handleSort = (field: 'score' | 'percentage' | 'submitted_at' | 'grade') => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const sortedStudents = [...(studentsRoster?.students || [])].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];

    if (valA === null || valA === undefined) valA = '';
    if (valB === null || valB === undefined) valB = '';

    if (typeof valA === 'number' && typeof valB === 'number') {
      return sortOrder === 'asc' ? valA - valB : valB - valA;
    }
    return sortOrder === 'asc'
      ? String(valA).localeCompare(String(valB))
      : String(valB).localeCompare(String(valA));
  });

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
          <BarChart2 className="w-8 h-8 text-emerald-400" /> Teacher Analytics & Exam Performance
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Comprehensive performance metrics, question discrimination accuracy, topic mastery, and student rosters.
        </p>
      </div>

      {/* Teacher Overview Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Question Papers</span>
          <div className="text-2xl font-black text-white">{summary?.total_question_papers || 0}</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Published Exams</span>
          <div className="text-2xl font-black text-emerald-400">{summary?.published_exams || 0}</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Active Assignments</span>
          <div className="text-2xl font-black text-indigo-400">{summary?.active_assignments || 0}</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Submissions</span>
          <div className="text-2xl font-black text-cyan-400">{summary?.total_submissions || 0}</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Average Score</span>
          <div className="text-2xl font-black text-amber-400">{summary?.average_score || 0}%</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Highest Score</span>
          <div className="text-2xl font-black text-emerald-400">{summary?.highest_score || 0}%</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Lowest Score</span>
          <div className="text-2xl font-black text-rose-400">{summary?.lowest_score || 0}%</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Pass Rate</span>
          <div className="text-2xl font-black text-emerald-400">{summary?.pass_percentage || 0}%</div>
        </div>
      </div>

      {/* Exam Selector */}
      <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-emerald-400" /> Select Exam for Detailed Performance Inspection
          </h2>
          <p className="text-xs text-slate-400">Inspect submission rates, itemized question difficulty, and student performance tables.</p>
        </div>

        <select
          value={selectedExamId}
          onChange={(e) => setSelectedExamId(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs font-semibold text-white focus:outline-none focus:border-emerald-500 min-w-[260px]"
        >
          {exams.length === 0 ? (
            <option value="">No exams available</option>
          ) : (
            exams.map((ex) => (
              <option key={ex.id} value={ex.id}>
                Class {ex.class_level} • {ex.subject} — {ex.title}
              </option>
            ))
          )}
        </select>
      </div>

      {loadingExamDetails ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-emerald-400 animate-spin" />
        </div>
      ) : examPerf && (
        <div className="space-y-8">
          {/* Exam Summary Metrics */}
          <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-xl font-black text-white">{examPerf.exam_title}</h3>
                <span className="text-xs text-slate-400">Class {examPerf.class_level} • Subject: {examPerf.subject}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Pass Rate: {examPerf.pass_rate}%
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Submissions: {examPerf.total_submissions} / {examPerf.assigned_students} ({examPerf.submission_percentage}%)
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-850">
                <span className="text-slate-400">Average Score</span>
                <div className="text-xl font-black text-amber-400 mt-1">{examPerf.average_score}%</div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-850">
                <span className="text-slate-400">Highest Score</span>
                <div className="text-xl font-black text-emerald-400 mt-1">{examPerf.highest_score}%</div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-850">
                <span className="text-slate-400">Lowest Score</span>
                <div className="text-xl font-black text-rose-400 mt-1">{examPerf.lowest_score}%</div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-850">
                <span className="text-slate-400">Topic Mastery</span>
                <div className="text-xl font-black text-indigo-400 mt-1">
                  {examPerf.topic_performance[0]?.mastery_percentage || 0}%
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-850">
                <span className="text-slate-400">Exact Topic</span>
                <div className="text-xs font-bold text-white mt-1 truncate">
                  {examPerf.topic_performance[0]?.topic || 'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Question-Wise Analytics */}
          {questionsAnalytics && (
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-indigo-400" /> Question-Wise Itemized Intelligence
              </h3>

              <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-950">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Q#</th>
                      <th className="px-4 py-3">Question Prompt</th>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Attempts</th>
                      <th className="px-4 py-3">Correct</th>
                      <th className="px-4 py-3">Incorrect</th>
                      <th className="px-4 py-3">Skipped</th>
                      <th className="px-4 py-3">Accuracy %</th>
                      <th className="px-4 py-3">Avg Marks</th>
                      <th className="px-4 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850 text-slate-300">
                    {questionsAnalytics.questions.map((q) => (
                      <tr key={q.question_id} className="hover:bg-slate-900/50">
                        <td className="px-4 py-3 font-bold text-white">Q{q.number}</td>
                        <td className="px-4 py-3 max-w-xs truncate text-slate-200" title={q.question}>{q.question}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-900 border border-slate-800 text-slate-400">
                            {q.question_type}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-white">{q.attempts_count}</td>
                        <td className="px-4 py-3 text-emerald-400 font-bold">{q.correct_count}</td>
                        <td className="px-4 py-3 text-rose-400 font-bold">{q.incorrect_count}</td>
                        <td className="px-4 py-3 text-slate-400 font-bold">{q.skipped_count}</td>
                        <td className="px-4 py-3 font-black text-indigo-400">{q.accuracy_percentage}%</td>
                        <td className="px-4 py-3 font-bold text-amber-400">{q.average_marks_awarded} / {q.maximum_marks}</td>
                        <td className="px-4 py-3">
                          {q.is_difficult ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                              <AlertCircle className="w-3 h-3" /> Difficult
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              <CheckCircle className="w-3 h-3" /> Normal
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Student Performance Roster */}
          {studentsRoster && (
            <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Users className="w-5 h-5 text-emerald-400" /> Student Examination Performance Roster
                </h3>
                <span className="text-xs text-slate-400 font-semibold">{sortedStudents.length} Candidate Records</span>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-950">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Student Email</th>
                      <th className="px-4 py-3 cursor-pointer select-none" onClick={() => handleSort('score')}>
                        <div className="flex items-center gap-1">Score <ArrowUpDown className="w-3 h-3" /></div>
                      </th>
                      <th className="px-4 py-3 cursor-pointer select-none" onClick={() => handleSort('percentage')}>
                        <div className="flex items-center gap-1">% Score <ArrowUpDown className="w-3 h-3" /></div>
                      </th>
                      <th className="px-4 py-3 cursor-pointer select-none" onClick={() => handleSort('grade')}>
                        <div className="flex items-center gap-1">Grade <ArrowUpDown className="w-3 h-3" /></div>
                      </th>
                      <th className="px-4 py-3 cursor-pointer select-none" onClick={() => handleSort('submitted_at')}>
                        <div className="flex items-center gap-1">Submitted At <ArrowUpDown className="w-3 h-3" /></div>
                      </th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Performance Flag</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850 text-slate-300">
                    {sortedStudents.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                          No student submissions recorded for this exam yet.
                        </td>
                      </tr>
                    ) : (
                      sortedStudents.map((st) => (
                        <tr key={st.attempt_id} className="hover:bg-slate-900/50">
                          <td className="px-4 py-3 font-bold text-white">{st.email}</td>
                          <td className="px-4 py-3 font-bold text-emerald-400">{st.score} / {st.max_score}</td>
                          <td className="px-4 py-3 font-black text-indigo-400">{st.percentage}%</td>
                          <td className="px-4 py-3 font-bold text-amber-400">{st.grade}</td>
                          <td className="px-4 py-3 text-slate-400">{st.submitted_at || 'N/A'}</td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              {st.evaluation_status}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-semibold">
                            {st.performance_flag === 'High Performer' && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">High Performer</span>
                            )}
                            {st.performance_flag === 'Average' && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">Average</span>
                            )}
                            {st.performance_flag === 'Needs Improvement' && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">Needs Improvement</span>
                            )}
                            {st.performance_flag === 'Not Submitted' && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Not Submitted</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
