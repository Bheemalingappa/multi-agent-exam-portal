import React from 'react';
import { Cpu, UserCheck, Shield, CheckCircle2, RefreshCw, Sparkles, Code2 } from 'lucide-react';

export const MultiAgentFlowDiagram: React.FC = () => {
  return (
    <div className="p-8 rounded-3xl bg-gradient-to-br from-indigo-950/60 via-slate-900 to-slate-950 border border-indigo-500/30 shadow-2xl space-y-8 relative overflow-hidden">
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
            <span>AI-POWERED EVALUATION PIPELINE</span>
          </div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Autonomous Agent-to-Agent (A2A) Consensus Engine
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
            When a student submits code or completes an assessment, specialized AI agents analyze functional correctness, code quality, execution latency, and security safety in parallel.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/80 px-4 py-2.5 rounded-xl border border-slate-800 text-xs text-emerald-400 font-semibold shadow-inner">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Real-time Scoring Verified</span>
        </div>
      </div>

      {/* Visual Pipeline Nodes */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative z-10">
        {/* Step 1: Submission */}
        <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="w-7 h-7 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold text-xs">1</span>
            <Code2 className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Student Submission</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">AST Parsing & Ephemeral Sandbox Execution</p>
          </div>
          <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 w-fit">HTTP 202 Queued</span>
        </div>

        {/* Step 2: Mentor Agent */}
        <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="w-7 h-7 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold text-xs">2</span>
            <UserCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Mentor Agent</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Code Readability & Architectural Quality</p>
          </div>
          <span className="text-[10px] font-semibold text-slate-300">Weight: 20%</span>
        </div>

        {/* Step 3: QA Auditor */}
        <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="w-7 h-7 rounded-lg bg-cyan-600/20 text-cyan-400 flex items-center justify-center font-bold text-xs">3</span>
            <Cpu className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">QA Auditor Agent</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Functional Test Cases & Boundary Validation</p>
          </div>
          <span className="text-[10px] font-semibold text-slate-300">Weight: 40%</span>
        </div>

        {/* Step 4: Security Agent */}
        <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="w-7 h-7 rounded-lg bg-rose-600/20 text-rose-400 flex items-center justify-center font-bold text-xs">4</span>
            <Shield className="w-5 h-5 text-rose-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Security Agent</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Module Import Restrictions & Memory Bounds</p>
          </div>
          <span className="text-[10px] font-semibold text-slate-300">Weight: 10%</span>
        </div>

        {/* Step 5: A2A Consensus Engine */}
        <div className="p-5 rounded-2xl bg-indigo-950/60 border border-indigo-500/40 flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="w-7 h-7 rounded-lg bg-amber-600/20 text-amber-400 flex items-center justify-center font-bold text-xs">5</span>
            <RefreshCw className="w-5 h-5 text-amber-400 animate-spin" style={{ animationDuration: '6s' }} />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Consensus Engine</h4>
            <p className="text-[11px] text-indigo-300 mt-0.5">A2A Negotiation Protocol & Score Reconciliation</p>
          </div>
          <span className="text-[10px] font-bold text-amber-300 bg-amber-500/20 px-2 py-0.5 rounded border border-amber-500/30 w-fit">Final Score Output</span>
        </div>
      </div>
    </div>
  );
};
