import React, { useState, useEffect } from 'react';
import { Activity, Cpu, Shield, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    axios
      .get('/api/health/components')
      .then((res) => setHealth(res.data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0a0f1d]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono font-medium text-slate-400">
          Academic Project:
        </span>
        <span className="text-xs font-semibold text-slate-200 bg-slate-800/80 border border-slate-700/60 px-2.5 py-1 rounded-md">
          AI Prompt Injection & Jailbreak Detection Firewall
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Gateway Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>Gateway Active</span>
        </div>

        {/* Model info */}
        <div className="hidden md:flex items-center gap-1.5 text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span>
            {health?.components?.ml_classifier?.model_version || 'TFIDF-LogReg-v1'}
          </span>
        </div>

        {/* Upstream LLM provider */}
        <div className="hidden lg:flex items-center gap-1.5 text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span>LLM: {health?.components?.llm_gateway?.default_provider || 'Mock Adapter'}</span>
        </div>
      </div>
    </header>
  );
};
