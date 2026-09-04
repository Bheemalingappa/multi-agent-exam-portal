import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getExamsApi } from '../../api/exams';
import { Exam } from '../../types/exam';
import { useAuth } from '../../auth/AuthProvider';
import { CLASS_CURRICULUM } from '../../config/curriculum';
import { BookOpen, Clock, Award, ArrowRight, ShieldCheck, AlertCircle, Loader2, GraduationCap, CheckCircle2, FileText, Sparkles, Filter, X, Layers, ChevronRight } from 'lucide-react';

export const CandidateDashboard: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const subjectParam = searchParams.get('subject');

  const selectedClassLevel = user?.class_level || undefined;
  const currentCurriculum = selectedClassLevel ? CLASS_CURRICULUM[selectedClassLevel] : null;

  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>(subjectParam || 'all');

  useEffect(() => {
    async function loadExams() {
      setLoading(true);
      setError('');
      try {
        const data = await getExamsApi({
          subject: selectedSubjectFilter !== 'all' ? selectedSubjectFilter : undefined
        });
        setExams(data);
      } catch (err: any) {
        setError(err.message || 'Failed loading class examinations.');
      } finally {
        setLoading(false);
      }
    }
    loadExams();
  }, [selectedClassLevel, selectedSubjectFilter]);

  useEffect(() => {
    if (subjectParam) {
      setSelectedSubjectFilter(subjectParam);
    }
  }, [subjectParam]);

  const clearFilters = () => {
    setSelectedSubjectFilter('all');
    setSearchParams({});
  };

  return (
    <div className="space-y-8 font-sans">
      {/* Top Banner / Student Greeting */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-500/30 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shadow-xl relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
            <GraduationCap className="w-4 h-4" />
            <span>{selectedClassLevel ? `CLASS ${selectedClassLevel} LEARNING TRACK` : 'CLASSES 1–12 CURRICULUM'}</span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">
            Good morning, {user?.email ? user.email.split('@')[0] : 'Student'}! 👋
          </h1>
          <p className="text-slate-300 text-sm max-w-xl leading-relaxed">
            {selectedClassLevel
              ? `Showing exams assigned to your registered Class ${selectedClassLevel}.`
              : 'Your student class is not configured. Please create a student account with a class level.'}
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-950/80 px-4 py-3 rounded-2xl border border-slate-800 text-xs text-slate-300 relative z-10">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <span className="font-bold text-white block">PostgreSQL Class Filter Active</span>
            <span className="text-[11px] text-slate-400">Strict Grade Isolation & Security</span>
          </div>
        </div>
      </div>

      {/* Registered Class Summary */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-emerald-400" /> Registered Academic Class
          </span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800">
          <span className="px-4 py-2 rounded-xl text-xs font-black shrink-0 border bg-gradient-to-r from-emerald-600 to-indigo-600 text-white border-emerald-400 shadow-lg shadow-emerald-600/30">
            {selectedClassLevel ? `Class ${selectedClassLevel}` : 'Class Not Set'}
          </span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Class Specific Subject Cards */}
      {currentCurriculum && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-emerald-400" /> Class {selectedClassLevel} Curriculum & Subjects
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {currentCurriculum.subjects.map((sub) => (
              <div
                key={sub.title}
                onClick={() => setSelectedSubjectFilter(sub.query)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between gap-3 ${
                  selectedSubjectFilter === sub.query
                    ? 'bg-slate-850 border-emerald-500 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      {sub.category}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-500" />
                  </div>
                  <h3 className="text-base font-bold text-white">{sub.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{sub.description}</p>
                </div>
                <span className="text-[11px] font-bold text-emerald-400">View Class {selectedClassLevel} {sub.title} Exams →</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assigned Exams Catalog */}
      <div id="exams" className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h2 className="text-xl font-black text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-emerald-400" />
            {selectedClassLevel ? `Exams Assigned to Class ${selectedClassLevel}` : 'Exams Assigned to You'} ({exams.length})
          </h2>

          {selectedSubjectFilter !== 'all' && (
            <div className="flex items-center gap-2 text-xs text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20">
              <span>Filter: {selectedSubjectFilter.toUpperCase()}</span>
              <X className="w-3.5 h-3.5 cursor-pointer" onClick={() => setSelectedSubjectFilter('all')} />
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[300px] gap-3">
            <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
            <p className="text-xs text-slate-400">Querying PostgreSQL for your assigned examinations...</p>
          </div>
        ) : exams.length === 0 ? (
          <div className="p-12 text-center bg-slate-900/60 rounded-2xl border border-slate-800 text-slate-400 space-y-4">
            <BookOpen className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-white">
              NO EXAMS ASSIGNED
            </h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Your teacher has not assigned any examinations to Class {selectedClassLevel || 'your class'} yet. Published exams will appear here once explicitly assigned to your class.
            </p>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={clearFilters}
                className="px-4 py-2 rounded-xl bg-slate-800 text-white text-xs font-bold hover:bg-slate-700"
              >
                Refresh Available Exams
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className="bg-slate-900 p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/50 transition-all flex flex-col justify-between gap-6 group hover:shadow-xl hover:shadow-emerald-500/10"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="px-3 py-1 text-[10px] font-black uppercase rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                      CLASS {exam.class_level || selectedClassLevel || 10} • {exam.subject || 'MATHEMATICS'}
                    </span>
                    <span className="text-xs text-slate-400 flex items-center gap-1 font-semibold">
                      <Clock className="w-3.5 h-3.5 text-slate-400" /> {exam.duration_minutes} mins
                    </span>
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-lg font-black text-white group-hover:text-emerald-300 transition-colors">
                      {exam.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">{exam.description}</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px] font-semibold uppercase">Difficulty / Score</span>
                    <span className="font-extrabold text-white capitalize">{exam.difficulty} • <span className="text-emerald-400">{exam.max_score} pts</span></span>
                  </div>
                  <Link
                    to={`/candidate/exams/${exam.id}`}
                    className="inline-flex items-center gap-2 text-xs font-bold bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white px-5 py-2.5 rounded-xl transition-all shadow-md shadow-emerald-600/20"
                  >
                    <span>View & Attempt</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
