import React from 'react';
import { Outlet } from 'react-router-dom';
import { EduNavbar } from '../components/common/EduNavbar';

export const RecruiterLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-indigo-500 selection:text-white">
      <EduNavbar />
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
        <Outlet />
      </main>
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>© 2026 EduExam — Educator & Assessment Management Suite</span>
          <span className="flex items-center gap-2 text-slate-400">
            <span>A2A Consensus Engine</span>
            <span>•</span>
            <span>Real-time Telemetry</span>
            <span>•</span>
            <span>AWS Infrastructure</span>
          </span>
        </div>
      </footer>
    </div>
  );
};
