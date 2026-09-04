import React, { useEffect, useState } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';

interface ExamTimerProps {
  expiresAt: string;
  onExpire?: () => void;
}

export const ExamTimer: React.FC<ExamTimerProps> = ({ expiresAt, onExpire }) => {
  const [secondsLeft, setSecondsLeft] = useState<number>(0);

  useEffect(() => {
    function updateTimer() {
      const exp = new Date(expiresAt).getTime();
      const now = new Date().getTime();
      const diff = Math.max(Math.floor((exp - now) / 1000), 0);
      setSecondsLeft(diff);

      if (diff === 0 && onExpire) {
        onExpire();
      }
    }

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [expiresAt, onExpire]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const isWarning = secondsLeft < 300; // < 5 minutes
  const isCritical = secondsLeft < 60; // < 1 minute

  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-lg border font-mono text-sm font-semibold transition-all ${
        isCritical
          ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-bounce'
          : isWarning
          ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 animate-pulse'
          : 'bg-slate-800 text-indigo-300 border-slate-700'
      }`}
    >
      {isWarning ? <AlertTriangle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
      <span>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
      {isWarning && <span className="text-xs font-sans text-amber-400 font-normal">Time Warning</span>}
    </div>
  );
};
