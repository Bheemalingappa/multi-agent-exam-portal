import React from 'react';
import { Cpu, DollarSign, Zap } from 'lucide-react';

export const AIUsagePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-6 h-6 text-indigo-400" /> AI Usage & Token Cost Tracking
        </h1>
        <p className="text-xs text-slate-400">Monitor token consumption, model latencies, and estimated provider costs across multi-agent evaluation tasks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-850 p-6 rounded-xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Total Tokens Processed</span>
          <p className="text-3xl font-extrabold text-white">142,850</p>
        </div>
        <div className="bg-slate-850 p-6 rounded-xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Estimated Provider Cost</span>
          <p className="text-3xl font-extrabold text-emerald-400">$0.499</p>
        </div>
        <div className="bg-slate-850 p-6 rounded-xl border border-slate-700 space-y-1">
          <span className="text-xs font-semibold text-slate-400 uppercase">Active Provider</span>
          <p className="text-3xl font-extrabold text-indigo-400">Gemini 1.5 Pro</p>
        </div>
      </div>
    </div>
  );
};
