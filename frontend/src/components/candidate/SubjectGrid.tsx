import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CLASS_CURRICULUM } from '../../config/curriculum';
import { Calculator, Atom, Flame, Dna, BookOpen, Globe2, Binary, ChevronRight, Layers } from 'lucide-react';

export const SubjectGrid: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const classParam = searchParams.get('class');
  const selectedClassLevel = classParam ? parseInt(classParam, 10) : undefined;
  const currentCurriculum = selectedClassLevel ? CLASS_CURRICULUM[selectedClassLevel] : null;

  const defaultSubjects = [
    { title: 'Mathematics', query: 'math', icon: Calculator, color: 'from-blue-500 to-indigo-600', desc: 'Algebra, Geometry, Quadratic Equations & Calculus' },
    { title: 'Science', query: 'science', icon: Atom, color: 'from-emerald-500 to-teal-600', desc: 'Natural World, Matter, Energy & Environmental Science' },
    { title: 'Physics', query: 'physics', icon: Flame, color: 'from-amber-500 to-rose-600', desc: 'Kinematics, Electromagnetism, Light & Quantum Mechanics' },
    { title: 'Chemistry', query: 'chemistry', icon: Atom, color: 'from-purple-500 to-indigo-600', desc: 'Chemical Reactions, Organic Chemistry & Periodic Table' },
    { title: 'Biology', query: 'biology', icon: Dna, color: 'from-green-500 to-emerald-600', desc: 'Human Physiology, Cell Biology, Genetics & Ecology' },
    { title: 'English', query: 'english', icon: BookOpen, color: 'from-rose-500 to-pink-600', desc: 'Grammar, Reading Comprehension, Literature & Writing' },
    { title: 'Social Studies', query: 'social', icon: Globe2, color: 'from-amber-600 to-yellow-500', desc: 'History, Geography, Political Science & Economics' },
    { title: 'Computer Science', query: 'python', icon: Binary, color: 'from-cyan-500 to-blue-600', desc: 'Python Programming, Algorithms, Logic & Data Structures' },
  ];

  const handleSelectSubject = (query: string) => {
    if (selectedClassLevel) {
      navigate(`/candidate?class=${selectedClassLevel}&subject=${query}`);
    } else {
      navigate(`/candidate?subject=${query}`);
    }
  };

  return (
    <div className="space-y-6">
      {selectedClassLevel && (
        <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between text-xs text-indigo-300">
          <span className="flex items-center gap-2 font-bold">
            <Layers className="w-4 h-4 text-indigo-400" /> Showing Class {selectedClassLevel} Curriculum Subjects ({currentCurriculum?.subjects.length})
          </span>
          <button
            onClick={() => navigate('/home/subjects')}
            className="text-slate-400 hover:text-white underline font-semibold"
          >
            Show All Subjects
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {defaultSubjects.map((sub) => {
          const Icon = sub.icon;
          return (
            <div
              key={sub.title}
              onClick={() => handleSelectSubject(sub.query)}
              className="group relative rounded-3xl border border-slate-800/90 bg-slate-900/70 p-6 hover:bg-slate-850 hover:border-emerald-500/50 transition-all duration-300 shadow-xl flex flex-col justify-between cursor-pointer"
            >
              <div>
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${sub.color} p-0.5 shadow-lg mb-4 group-hover:scale-110 transition-transform`}>
                  <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <h4 className="text-base font-black text-white group-hover:text-emerald-300 transition-colors">
                  {sub.title}
                </h4>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {sub.desc}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-extrabold text-slate-400 group-hover:text-emerald-400">
                <span>View {selectedClassLevel ? `Class ${selectedClassLevel}` : ''} Exams</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
