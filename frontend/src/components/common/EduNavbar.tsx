import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthProvider';
import { 
  GraduationCap, 
  Sparkles, 
  BookOpen, 
  PlusCircle, 
  LayoutDashboard, 
  BarChart3, 
  History, 
  LogOut, 
  User, 
  Menu, 
  X,
  CheckCircle2
} from 'lucide-react';

export const EduNavbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-indigo-500 to-amber-400 p-0.5 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <span className="text-lg font-black tracking-tight text-white flex items-center gap-1.5">
                EduExam <span className="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Class 1–12</span>
              </span>
              <p className="text-[10px] font-medium text-slate-400 hidden sm:block">Smart Learning & Assessment Platform</p>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden lg:flex items-center gap-1 text-xs font-semibold">
            <Link
              to="/home"
              className={`px-3 py-2 rounded-lg transition-colors ${
                isActive('/') || isActive('/home')
                  ? 'bg-slate-900 text-emerald-400 border border-slate-800'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              Home
            </Link>

            {user?.role === 'candidate' && (
              <>
                <Link
                  to="/candidate"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/candidate')
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4" /> Available Exams
                </Link>
                <Link
                  to="/candidate/results"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/candidate/results')
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <History className="w-4 h-4" /> Results History
                </Link>
              </>
            )}

            {(user?.role === 'recruiter' || user?.role === 'admin') && (
              <>
                <Link
                  to="/recruiter"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/recruiter')
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4" /> Educator Overview
                </Link>
                <Link
                  to="/recruiter/question-papers/generate"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/recruiter/question-papers/generate')
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-amber-400" /> AI Paper Generator
                </Link>
                <Link
                  to="/recruiter/question-papers"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/recruiter/question-papers')
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <BookOpen className="w-4 h-4" /> Question Papers Bank
                </Link>
                <Link
                  to="/recruiter/analytics"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                    isActive('/recruiter/analytics')
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <BarChart3 className="w-4 h-4" /> Analytics
                </Link>
              </>
            )}
          </nav>

          {/* User Profile & Actions */}
          <div className="hidden sm:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl">
                  <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
                    {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-slate-200 max-w-[120px] truncate">{user.email}</p>
                    <p className="text-[10px] font-bold uppercase text-emerald-400">{user.role}</p>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="p-2.5 rounded-xl bg-slate-900 hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 border border-slate-800 hover:border-rose-500/30 transition-all"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-900 border border-slate-800 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 to-indigo-600 hover:from-emerald-400 hover:to-indigo-500 text-white shadow-lg shadow-emerald-500/25 transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2.5 rounded-xl bg-slate-900 text-slate-300 hover:text-white border border-slate-800"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-950/95 backdrop-blur-xl px-4 pt-3 pb-6 space-y-3">
          <Link
            to="/home"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900"
          >
            Home
          </Link>
          {user?.role === 'candidate' && (
            <>
              <Link
                to="/candidate"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
              >
                Available Exams
              </Link>
              <Link
                to="/candidate/results"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900"
              >
                Results History
              </Link>
            </>
          )}
          {(user?.role === 'recruiter' || user?.role === 'admin') && (
            <>
              <Link
                to="/recruiter"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900"
              >
                Educator Overview
              </Link>
              <Link
                to="/recruiter/question-papers/generate"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-semibold text-amber-400 bg-amber-500/10 border border-amber-500/20"
              >
                ✨ AI Paper Generator
              </Link>
              <Link
                to="/recruiter/question-papers"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900"
              >
                Question Papers Bank
              </Link>
            </>
          )}
          {user ? (
            <button
              onClick={handleLogout}
              className="w-full text-left px-3 py-2 rounded-lg text-sm font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 flex items-center justify-between"
            >
              <span>Sign Out ({user.email})</span>
              <LogOut className="w-4 h-4" />
            </button>
          ) : (
            <div className="pt-2 flex flex-col gap-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 rounded-xl text-xs font-bold text-slate-300 bg-slate-900 border border-slate-800"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 rounded-xl text-xs font-bold bg-emerald-600 text-white"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
