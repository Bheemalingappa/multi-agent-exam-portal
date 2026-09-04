import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Sparkles, ChevronRight, ShieldCheck } from 'lucide-react';

export const ClassSelectionGrid: React.FC = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'primary' | 'middle' | 'high'>('all');

  const classes = [
    { level: 1, category: 'primary', title: 'Class 1', desc: 'Foundational Numbers, Alphabet & Environmental Awareness', subjects: 4 },
    { level: 2, category: 'primary', title: 'Class 2', desc: 'Basic Addition, Subtraction & Language Building', subjects: 4 },
    { level: 3, category: 'primary', title: 'Class 3', desc: 'Introductory Multiplication, Science & Social Science', subjects: 5 },
    { level: 4, category: 'primary', title: 'Class 4', desc: 'Division, Fractions & General Knowledge Assessments', subjects: 5 },
    { level: 5, category: 'primary', title: 'Class 5', desc: 'Primary Board Prep, Mathematics & Natural Science', subjects: 6 },
    { level: 6, category: 'middle', title: 'Class 6', desc: 'Integers, Physics Fundamentals & Earth Studies', subjects: 6 },
    { level: 7, category: 'middle', title: 'Class 7', desc: 'Algebraic Expressions, Chemistry & Medieval History', subjects: 6 },
    { level: 8, category: 'middle', title: 'Class 8', desc: 'Linear Equations, Force & Pressure, Computer Logic', subjects: 7 },
    { level: 9, category: 'high', title: 'Class 9', desc: 'Polynomials, Motion, Atoms & World History', subjects: 8 },
    { level: 10, category: 'high', title: 'Class 10', desc: 'Quadratic Equations, Light, Trigonometry & Board Exams', subjects: 8 },
    { level: 11, category: 'high', title: 'Class 11', desc: 'Calculus, Electromagnetism, Organic Chemistry & CS', subjects: 8 },
    { level: 12, category: 'high', title: 'Class 12', desc: 'Higher Mathematics, Quantum Physics & AI Assessment', subjects: 8 },
  ];

  const filtered = selectedCategory === 'all' 
    ? classes 
    : classes.filter(c => c.category === selectedCategory);

  const handleSelectClass = (level: number) => {
    navigate(`/candidate?class=${level}`);
  };

  return (
    <div className="space-y-6">
      {/* Category Tabs */}
      <div className="flex flex-wrap items-center justify-center gap-2">
        {[
          { id: 'all', label: 'All Classes (1–12)' },
          { id: 'primary', label: 'Primary (Class 1–5)' },
          { id: 'middle', label: 'Middle School (Class 6–8)' },
          { id: 'high', label: 'High School (Class 9–12)' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedCategory(tab.id as any)}
            className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all border ${
              selectedCategory === tab.id
                ? 'bg-gradient-to-r from-emerald-500 to-indigo-600 text-white border-emerald-400/50 shadow-lg shadow-emerald-500/20 scale-105'
                : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((cls) => (
          <div
            key={cls.level}
            onClick={() => handleSelectClass(cls.level)}
            className="group relative rounded-3xl border border-slate-800/90 bg-slate-900/60 p-5 hover:bg-slate-850 hover:border-emerald-500/40 transition-all duration-300 shadow-xl flex flex-col justify-between cursor-pointer"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500/20 to-indigo-500/20 border border-emerald-500/30 text-emerald-400 font-black text-sm flex items-center justify-center group-hover:scale-110 transition-transform">
                  C{cls.level}
                </span>
                <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-slate-400">
                  {cls.subjects} Subjects
                </span>
              </div>
              <h3 className="text-lg font-black text-white group-hover:text-emerald-300 transition-colors">
                {cls.title}
              </h3>
              <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                {cls.desc}
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-500 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Syllabus Aligned
              </span>
              <button
                type="button"
                className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-400 group-hover:translate-x-1 transition-transform"
              >
                Explore <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
