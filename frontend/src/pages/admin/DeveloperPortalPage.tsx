import React, { useState } from 'react';
import { Code, Key, Webhook, FileText, Copy, CheckCircle2 } from 'lucide-react';

export const DeveloperPortalPage: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const sampleKey = "mae_live_x9Fk21Lp09aZqWvNm38190XyZ";

  const handleCopy = () => {
    navigator.clipboard.writeText(sampleKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Code className="w-6 h-6 text-sky-400" /> Developer Platform & Public API Portal
        </h1>
        <p className="text-xs text-slate-400">Manage scoped organization API keys, register webhook event subscribers, and view OpenAPI specifications.</p>
      </div>

      <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs uppercase font-semibold text-slate-400 flex items-center gap-1.5">
            <Key className="w-4 h-4 text-amber-400" /> Production API Secret Key
          </span>
          <span className="text-xs text-slate-400">Scoped: exam:read, submission:read, analytics:read</span>
        </div>

        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between font-mono text-xs text-amber-300">
          <span>{sampleKey}</span>
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
