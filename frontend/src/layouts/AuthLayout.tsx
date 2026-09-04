import React from 'react';
import { Outlet } from 'react-router-dom';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 sm:p-6 lg:p-8 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white">
      <div className="w-full max-w-5xl">
        <Outlet />
      </div>
    </div>
  );
};
