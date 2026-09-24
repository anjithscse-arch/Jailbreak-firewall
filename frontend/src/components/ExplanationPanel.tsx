import React from 'react';
import { Explanation } from '../types/firewall';
import { Info, AlertCircle, CheckCircle2, Lightbulb } from 'lucide-react';

interface ExplanationPanelProps {
  explanation: Explanation;
  decision: 'ALLOW' | 'BLOCK' | 'REVIEW';
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  explanation,
  decision,
}) => {
  const isBlock = decision === 'BLOCK';

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-900/80 p-5 backdrop-blur-sm space-y-4">
      <div className="flex items-start gap-3">
        {isBlock ? (
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
        ) : decision === 'REVIEW' ? (
          <Info className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        ) : (
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        )}
        <div>
          <h4 className="text-sm font-semibold text-slate-200">Decision Rationale</h4>
          <p className="text-sm text-slate-300 mt-1 leading-relaxed">{explanation.summary}</p>
        </div>
      </div>

      {/* Structured Reasons */}
      {explanation.reasons && explanation.reasons.length > 0 && (
        <div className="space-y-1.5 pl-8">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
            Identified Factors:
          </span>
          <ul className="list-disc list-outside text-xs text-slate-300 space-y-1 pl-4">
            {explanation.reasons.map((reason, idx) => (
              <li key={idx} className="leading-normal">{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Remediation guidance */}
      {explanation.recommended_action && (
        <div className="flex items-start gap-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20 p-3 text-xs text-blue-300">
          <Lightbulb className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-blue-200 mb-0.5">Recommended Remediation:</span>
            {explanation.recommended_action}
          </div>
        </div>
      )}
    </div>
  );
};
