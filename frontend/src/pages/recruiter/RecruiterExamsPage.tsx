import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getExamsApi, publishExamApi, unpublishExamApi } from '../../api/exams';
import { Exam } from '../../types/exam';
import { FileSpreadsheet, Plus, Activity, Edit3, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export const RecruiterExamsPage: React.FC = () => {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  const loadExams = async () => {
    try {
      const data = await getExamsApi();
      setExams(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExams();
  }, []);

  const handleTogglePublish = async (exam: Exam) => {
    if (exam.is_published) {
      await unpublishExamApi(exam.id);
    } else {
      await publishExamApi(exam.id);
    }
    loadExams();
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
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-emerald-400" /> Exam Catalog Management
          </h1>
          <p className="text-xs text-slate-400">Publish exams to candidates or edit question bank details.</p>
        </div>

        <Link
          to="/recruiter/exams/create"
          className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-xl transition-colors text-sm"
        >
          <Plus className="w-4 h-4" /> Create Assessment
        </Link>
      </div>

      <div className="bg-slate-850 rounded-xl border border-slate-700 overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900 text-xs font-semibold uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4">Exam Title</th>
              <th className="px-6 py-4">Difficulty</th>
              <th className="px-6 py-4">Duration</th>
              <th className="px-6 py-4">Max Score</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {exams.map((exam) => (
              <tr key={exam.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-6 py-4 font-semibold text-white">{exam.title}</td>
                <td className="px-6 py-4 uppercase text-xs font-medium text-slate-400">{exam.difficulty}</td>
                <td className="px-6 py-4 text-xs">{exam.duration_minutes} mins</td>
                <td className="px-6 py-4 text-xs">{exam.max_score} pts</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                    exam.is_published ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {exam.is_published ? 'Published' : 'Draft'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                  <button
                    onClick={() => handleTogglePublish(exam)}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold transition-colors"
                  >
                    {exam.is_published ? 'Unpublish' : 'Publish'}
                  </button>
                  <Link
                    to={`/recruiter/exams/${exam.id}/questions`}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-400 transition-colors"
                    title="Manage Question Bank"
                  >
                    <Edit3 className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/recruiter/exams/${exam.id}/live`}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-400 transition-colors"
                    title="Live Monitor"
                  >
                    <Activity className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
