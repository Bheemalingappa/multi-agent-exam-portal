import React from 'react';
import { BookOpen, Sparkles, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface ClassItem {
  id: number;
  name: string;
  category: 'Primary' | 'Middle' | 'Secondary' | 'Senior Secondary';
  description: string;
  subjectCount: number;
  badgeColor: string;
}

const CLASSES: ClassItem[] = [
  { id: 1, name: 'Class 1', category: 'Primary', description: 'Foundational literacy, basic arithmetic & fun science', subjectCount: 4, badgeColor: 'from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/30' },
  { id: 2, name: 'Class 2', category: 'Primary', description: 'Interactive reading, numbers & environmental studies', subjectCount: 4, badgeColor: 'from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/30' },
  { id: 3, name: 'Class 3', category: 'Primary', description: 'Language building, mental math & nature explorations', subjectCount: 5, badgeColor: 'from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/30' },
  { id: 4, name: 'Class 4', category: 'Primary', description: 'Grammar, science experiments & geography basics', subjectCount: 5, badgeColor: 'from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/30' },
  { id: 5, name: 'Class 5', category: 'Primary', description: 'Primary completion assessment & logical reasoning', subjectCount: 5, badgeColor: 'from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/30' },
  { id: 6, name: 'Class 6', category: 'Middle', description: 'Algebra fundamentals, general science & history', subjectCount: 6, badgeColor: 'from-cyan-500/20 to-blue-500/20 text-cyan-300 border-cyan-500/30' },
  { id: 7, name: 'Class 7', category: 'Middle', description: 'Geometry, physics concepts & computer basics', subjectCount: 6, badgeColor: 'from-cyan-500/20 to-blue-500/20 text-cyan-300 border-cyan-500/30' },
  { id: 8, name: 'Class 8', category: 'Middle', description: 'Advanced math, chemistry & introductory coding', subjectCount: 6, badgeColor: 'from-cyan-500/20 to-blue-500/20 text-cyan-300 border-cyan-500/30' },
  { id: 9, name: 'Class 9', category: 'Secondary', description: 'High school foundation, biology & Python programming', subjectCount: 7, badgeColor: 'from-emerald-500/20 to-teal-500/20 text-emerald-300 border-emerald-500/30' },
  { id: 10, name: 'Class 10', category: 'Secondary', description: 'Board Exam Preparation, mock tests & proctored practice', subjectCount: 7, badgeColor: 'from-emerald-500/20 to-teal-500/20 text-emerald-300 border-emerald-500/30' },
  { id: 11, name: 'Class 11', category: 'Senior Secondary', description: 'Stream specialization: PCM/PCB/Commerce/Humanities & CS', subjectCount: 8, badgeColor: 'from-indigo-500/20 to-purple-500/20 text-indigo-300 border-indigo-500/30' },
  { id: 12, name: 'Class 12', category: 'Senior Secondary', description: 'Senior Board Mastery, competitive entrance & AI evaluation', subjectCount: 8, badgeColor: 'from-indigo-500/20 to-purple-500/20 text-indigo-300 border-indigo-500/30' },
];

interface Props {
  selectedClass: number | null;
  onSelectClass: (classId: number) => void;
}

export const ClassSelectionGrid: React.FC<Props> = ({ selectedClass, onSelectClass }) => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-emerald-400" />
            Class 1 to Class 12 Learning Tracks
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Select a class level to view specialized curriculum subjects, mock tests, and assessments.
          </p>
        </div>

        {selectedClass && (
          <button
            onClick={() => onSelectClass(0)}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
          >
            Show All Classes
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {CLASSES.map((cls) => {
          const isSelected = selectedClass === cls.id;
          return (
            <div
              key={cls.id}
              onClick={() => onSelectClass(cls.id)}
              className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between gap-4 group ${
                isSelected
                  ? 'bg-slate-900 border-emerald-500 shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500'
                  : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase border bg-gradient-to-r ${cls.badgeColor}`}>
                    {cls.name}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-400" /> {cls.subjectCount} Subjects
                  </span>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">{cls.category}</span>
                  <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors flex items-center justify-between">
                    <span>{cls.name} Curriculum</span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                  </h3>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{cls.description}</p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold">
                <span className="text-slate-400 group-hover:text-slate-300">
                  {cls.id >= 10 ? 'Board Exam Prep' : 'Interactive Track'}
                </span>
                <span className="text-emerald-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  Explore <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
