import React from 'react';
import { Eye } from 'lucide-react';

interface ProctoringIndicatorProps {
  connected?: boolean;
}

export const ProctoringIndicator: React.FC<ProctoringIndicatorProps> = ({ connected = true }) => {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-300">
      <span className="relative flex h-2 w-2">
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
            connected ? 'bg-emerald-400' : 'bg-amber-400'
          }`}
        />
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            connected ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
        />
      </span>
      <Eye className="w-3.5 h-3.5 text-slate-400" />
      <span>Proctoring Monitoring Active</span>
    </div>
  );
};
