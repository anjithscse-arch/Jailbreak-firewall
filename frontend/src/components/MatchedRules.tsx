import React from 'react';
import { MatchedRule } from '../types/firewall';
import { ShieldCheck, AlertOctagon } from 'lucide-react';

interface MatchedRulesProps {
  rules: MatchedRule[];
}

export const MatchedRules: React.FC<MatchedRulesProps> = ({ rules }) => {
  if (!rules || rules.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-center">
        <ShieldCheck className="w-6 h-6 text-slate-500 mx-auto mb-1.5" />
        <p className="text-xs text-slate-400 font-mono">No deterministic Layer 1 rules triggered.</p>
      </div>
    );
  }

  const severityBadges = {
    CRITICAL: 'bg-red-500/20 text-red-300 border-red-500/40',
    HIGH: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
    MEDIUM: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    LOW: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
  };

  return (
    <div className="space-y-2.5">
      <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
        <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
        Matched Layer 1 Rules ({rules.length})
      </h4>
      <div className="space-y-2">
        {rules.map((rule, idx) => (
          <div
            key={idx}
            className="rounded-lg border border-slate-700/80 bg-slate-800/60 p-3.5 transition hover:border-slate-600"
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="font-mono text-xs font-bold text-slate-200">
                {rule.rule_id}: {rule.name}
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-semibold ${
                  severityBadges[rule.severity] || severityBadges.MEDIUM
                }`}
              >
                {rule.severity} ({rule.score.toFixed(2)})
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-normal">{rule.description}</p>
            {rule.matched_text && (
              <div className="mt-2 rounded bg-slate-950/80 border border-slate-800 px-2.5 py-1.5 text-xs font-mono text-rose-300 break-all">
                <span className="text-slate-500 text-[10px] uppercase block">Matched Fragment:</span>
                "{rule.matched_text}"
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
