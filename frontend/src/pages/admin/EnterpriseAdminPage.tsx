import React from 'react';
import { Building2, Key, ToggleRight, Server, ShieldCheck, Database } from 'lucide-react';

export const EnterpriseAdminPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Building2 className="w-6 h-6 text-indigo-400" /> Enterprise Admin & SaaS Governance
        </h1>
        <p className="text-xs text-slate-400">Configure Identity Providers (OIDC/SAML), SCIM Provisioning, Feature Flags, and Multi-Region Health.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-2">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
            <Key className="w-4 h-4" /> Identity Provider (SSO)
          </div>
          <p className="text-xs text-slate-400">SAML 2.0 / OIDC Enabled</p>
          <span className="inline-block px-2.5 py-1 text-xs font-bold bg-emerald-500/20 text-emerald-300 rounded-full">ACTIVE</span>
        </div>

        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-2">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
            <ToggleRight className="w-4 h-4" /> SCIM Provisioning
          </div>
          <p className="text-xs text-slate-400">Automated User Lifecycle</p>
          <span className="inline-block px-2.5 py-1 text-xs font-bold bg-emerald-500/20 text-emerald-300 rounded-full">ENABLED</span>
        </div>

        <div className="bg-slate-850 p-6 rounded-2xl border border-slate-700 space-y-2">
          <div className="flex items-center gap-2 text-rose-400 font-semibold text-sm">
            <Server className="w-4 h-4" /> Multi-Region Status
          </div>
          <p className="text-xs text-slate-400">us-east-1 / us-west-2</p>
          <span className="inline-block px-2.5 py-1 text-xs font-bold bg-emerald-500/20 text-emerald-300 rounded-full">HEALTHY</span>
        </div>
      </div>
    </div>
  );
};
