import React from 'react';
import { Calculator, Atom, BookText, Globe, Terminal, BrainCircuit, ArrowRight, Award } from 'lucide-react';

export interface SubjectItem {
  id: string;
  name: string;
  icon: React.ReactNode;
  examCount: number;
  progressPercent: number;
  description: string;
  color: string;
}

const SUBJECTS: SubjectItem[] = [
  { id: 'math', name: 'Mathematics', icon: <Calculator className="w-6 h-6 text-amber-400" />, examCount: 14, progressPercent: 82, description: 'Algebra, Geometry, Arithmetic, Trigonometry & Calculus', color: 'border-amber-500/30 bg-amber-500/10' },
  { id: 'science', name: 'Science', icon: <Atom className="w-6 h-6 text-cyan-400" />, examCount: 12, progressPercent: 74, description: 'Physics, Chemistry, Biology & Environmental Studies', color: 'border-cyan-500/30 bg-cyan-500/10' },
  { id: 'english', name: 'English Literature & Grammar', icon: <BookText className="w-6 h-6 text-emerald-400" />, examCount: 10, progressPercent: 88, description: 'Reading Comprehension, Essay Writing & Grammar Mastery', color: 'border-emerald-500/30 bg-emerald-500/10' },
  { id: 'social', name: 'Social Studies', icon: <Globe className="w-6 h-6 text-rose-400" />, examCount: 8, progressPercent: 68, description: 'History, Civics, Geography & Economics', color: 'border-rose-500/30 bg-rose-500/10' },
  { id: 'cs', name: 'Computer Science & Coding', icon: <Terminal className="w-6 h-6 text-indigo-400" />, examCount: 16, progressPercent: 92, description: 'Python, Algorithms, Data Structures & AST Module Bans', color: 'border-indigo-500/30 bg-indigo-500/10' },
  { id: 'gk', name: 'General Knowledge & Logic', icon: <BrainCircuit className="w-6 h-6 text-purple-400" />, examCount: 6, progressPercent: 95, description: 'Current Affairs, Mental Aptitude & Reasoning Tests', color: 'border-purple-500/30 bg-purple-500/10' },
];

interface Props {
  selectedSubject: string | null;
  onSelectSubject: (subjectId: string) => void;
}

export const SubjectGrid: React.FC<Props> = ({ selectedSubject, onSelectSubject }) => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Award className="w-6 h-6 text-indigo-400" />
            Academic Subjects & Core Disciplines
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Choose a subject to filter online examinations, practice papers, and AI-evaluated code assessments.
          </p>
        </div>

        {selectedSubject && (
          <button
            onClick={() => onSelectSubject('')}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
          >
            Show All Subjects
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {SUBJECTS.map((sub) => {
          const isSelected = selectedSubject === sub.id;
          return (
            <div
              key={sub.id}
              onClick={() => onSelectSubject(sub.id)}
              className={`p-6 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between gap-5 group ${
                isSelected
                  ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500'
                  : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
              }`}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-xl border ${sub.color}`}>
                    {sub.icon}
                  </div>
                  <span className="text-xs font-semibold text-slate-400 px-2.5 py-1 rounded-md bg-slate-950 border border-slate-800">
                    {sub.examCount} Exams Available
                  </span>
                </div>

                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                    {sub.name}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{sub.description}</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-medium">Student Proficiency</span>
                  <span className="text-indigo-400 font-bold">{sub.progressPercent}%</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${sub.progressPercent}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-xs font-semibold pt-1 text-indigo-400 group-hover:translate-x-0.5 transition-transform">
                <span>Explore Assessments</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
