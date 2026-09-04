import React from 'react';
import DOMPurify from 'dompurify';

interface ExplainThenGradeReportProps {
  reportMarkdown?: string;
  finalScore?: number;
}

export const ExplainThenGradeReport: React.FC<ExplainThenGradeReportProps> = ({
  reportMarkdown,
  finalScore,
}) => {
  if (!reportMarkdown) {
    return (
      <div className="p-6 bg-slate-850 rounded-xl border border-slate-700 text-slate-400 text-center">
        No evaluation report generated yet.
      </div>
    );
  }

  // Simple HTML formatting for Markdown sections
  const formattedHtml = reportMarkdown
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-white mb-4 border-b border-slate-700 pb-2">$1</h1>')
    .replace(/^## (.*$)/gim, '<h2 class="text-lg font-semibold text-indigo-300 mt-6 mb-3">$1</h2>')
    .replace(/^### (.*$)/gim, '<h3 class="text-md font-medium text-emerald-300 mt-4 mb-2">$1</h3>')
    .replace(/^\> (.*$)/gim, '<blockquote class="border-l-4 border-indigo-500 bg-indigo-950/30 p-4 rounded-r-lg text-slate-200 my-4">$1</blockquote>')
    .replace(/`- (.*$)/gim, '<li class="ml-4 text-slate-300 list-disc">$1</li>')
    .replace(/\n\n/g, '<br/>');

  const cleanHtml = DOMPurify.sanitize(formattedHtml);

  return (
    <div className="bg-slate-850 p-8 rounded-xl border border-slate-700 shadow-2xl space-y-6">
      {finalScore !== undefined && (
        <div className="flex items-center justify-between p-4 rounded-lg bg-indigo-950/40 border border-indigo-500/40">
          <div>
            <span className="text-xs uppercase font-semibold text-indigo-400 tracking-wider">A2A Consensus Score</span>
            <p className="text-3xl font-extrabold text-white">{finalScore} <span className="text-sm font-normal text-slate-400">/ 100</span></p>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">Evaluation Mode</span>
            <p className="text-sm font-medium text-emerald-400">Explain-Then-Grade Paradigm</p>
          </div>
        </div>
      )}

      <div
        className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed"
        dangerouslySetInnerHTML={{ __html: cleanHtml }}
      />
    </div>
  );
};
