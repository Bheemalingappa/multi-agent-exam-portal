import React from 'react';
import { Lightbulb, CheckCircle2, HelpCircle, AlertCircle } from 'lucide-react';

export const QuestionIntelligencePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-yellow-400" /> Question Intelligence & Quality Analytics
        </h1>
        <p className="text-xs text-slate-400">Analyze question difficulty, discrimination indices, and candidate completion latencies to optimize test quality.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Questions Analyzed</span>
          <p className="text-3xl font-extrabold text-white">12</p>
        </div>
        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Highly Discriminative</span>
          <p className="text-3xl font-extrabold text-emerald-400">5 Questions</p>
        </div>
        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Avg Completion Latency</span>
          <p className="text-3xl font-extrabold text-indigo-400">145.2s</p>
        </div>
      </div>
    </div>
  );
};
