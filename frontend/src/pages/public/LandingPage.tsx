import React from 'react';
import { Link } from 'react-router-dom';
import { EduNavbar } from '../../components/common/EduNavbar';
import { ClassSelectionGrid } from '../../components/candidate/ClassSelectionGrid';
import { SubjectGrid } from '../../components/candidate/SubjectGrid';
import { MultiAgentFlowDiagram } from '../../components/edu/MultiAgentFlowDiagram';

import { Sparkles, ArrowRight, ShieldCheck, Cpu, Award, BookOpen, CheckCircle2, Bot } from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-emerald-500 selection:text-white">
      <EduNavbar />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden pt-12 sm:pt-20 pb-16 sm:pb-24 border-b border-slate-800/80">
          {/* Background Ambient Glows */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-emerald-500/10 via-indigo-500/10 to-amber-500/10 blur-[120px] pointer-events-none rounded-full" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
            
            {/* Top Pill Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900 border border-slate-800 text-xs font-extrabold text-slate-300 mb-8 shadow-xl">
              <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
              <span>Next-Gen EdTech Assessment Engine</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span className="text-emerald-400 font-extrabold uppercase text-[10px]">Class 1–12 Ready</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-white tracking-tight leading-[1.1] max-w-4xl mx-auto">
              Smart Learning.{' '}
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
                Smarter Assessments.
              </span>
            </h1>

            {/* Sub-headline */}
            <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mt-6 leading-relaxed">
              Empowering Class 1 through Class 12 students with AI-assisted examination paper generation, step-by-step mathematical solution keys, and real-time Multi-Agent consensus grading.
            </p>

            {/* Call to Actions */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="#classes"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-indigo-600 hover:from-emerald-400 hover:to-indigo-500 text-white font-extrabold px-8 py-4 rounded-2xl transition-all shadow-xl shadow-emerald-500/25 text-sm"
              >
                Explore Classes <ArrowRight className="w-4 h-4" />
              </a>
              <Link
                to="/register"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-850 text-slate-200 hover:text-white font-extrabold px-8 py-4 rounded-2xl transition-all border border-slate-800 text-sm"
              >
                Get Started Free
              </Link>
            </div>

            {/* Verified Feature Bar */}
            <div className="mt-16 pt-10 border-t border-slate-900 grid grid-cols-2 md:grid-cols-4 gap-4 text-center max-w-4xl mx-auto">
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/60">
                <p className="text-2xl font-black text-white">Class 1–12</p>
                <p className="text-xs font-semibold text-slate-400 mt-1">Full Curriculum Coverage</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/60">
                <p className="text-2xl font-black text-emerald-400">100% Valid</p>
                <p className="text-xs font-semibold text-slate-400 mt-1">Section Marks Balancing</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/60">
                <p className="text-2xl font-black text-indigo-400">3 AI Agents</p>
                <p className="text-xs font-semibold text-slate-400 mt-1">Consensus Grading Engine</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/60">
                <p className="text-2xl font-black text-amber-400">LaTeX Math</p>
                <p className="text-xs font-semibold text-slate-400 mt-1">KaTeX Formula Rendering</p>
              </div>
            </div>

          </div>
        </section>

        {/* Class Selection Section */}
        <section id="classes" className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-b border-slate-800/80">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-extrabold uppercase tracking-widest text-emerald-400">Grade Level Catalog</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">Class 1 through Class 12 Learning Tracks</h2>
            <p className="text-slate-400 text-sm mt-3">Select your grade level to discover subject practice tests, question paper drafts, and exam formats.</p>
          </div>
          <ClassSelectionGrid />
        </section>

        {/* Subjects Section */}
        <section id="subjects" className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-b border-slate-800/80">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-extrabold uppercase tracking-widest text-indigo-400">Comprehensive Subjects</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">Master All Key Disciplines</h2>
            <p className="text-slate-400 text-sm mt-3">From Mathematics quadratic derivations to Physics electromagnetism and CS logic.</p>
          </div>
          <SubjectGrid />
        </section>

        {/* Multi-Agent Architecture Section */}
        <section className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-extrabold uppercase tracking-widest text-amber-400">AI Evaluation Architecture</span>
            <h2 className="text-3xl sm:text-4xl font-black text-white mt-2">Multi-Agent Consensus Scoring Engine</h2>
            <p className="text-slate-400 text-sm mt-3">Every student submission is evaluated in parallel by specialized AI agents ensuring transparent, bias-free scorecards.</p>
          </div>
          <MultiAgentFlowDiagram />
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-8 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="font-semibold text-slate-400">© 2026 EduExam — Smart Learning & Assessment Platform</span>
          <div className="flex items-center gap-3 text-slate-400">
            <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> AWS EKS Active</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5 text-indigo-400" /> RDS PostgreSQL Star Schema</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
