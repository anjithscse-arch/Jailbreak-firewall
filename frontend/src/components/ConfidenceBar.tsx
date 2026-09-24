import React from 'react';

interface ConfidenceBarProps {
  score: number; // 0.0 to 1.0
  label?: string;
  showPercent?: boolean;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({
  score,
  label = 'Risk Score',
  showPercent = true,
}) => {
  const percent = Math.min(100, Math.max(0, Math.round(score * 100)));

  // Color mapping based on risk
  let barColor = 'from-emerald-500 to-teal-400';
  let textColor = 'text-emerald-400';

  if (percent >= 70) {
    barColor = 'from-rose-600 to-red-500';
    textColor = 'text-rose-400';
  } else if (percent >= 45) {
    barColor = 'from-amber-500 to-yellow-400';
    textColor = 'text-amber-400';
  }

  return (
    <div className="w-full">
      <div className="flex justify-between items-center text-xs mb-1.5 font-mono">
        <span className="text-slate-400">{label}</span>
        {showPercent && (
          <span className={`font-semibold ${textColor}`}>
            {percent}% ({score.toFixed(3)})
          </span>
        )}
      </div>
      <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
        <div
          className={`h-full bg-gradient-to-r ${barColor} transition-all duration-500 ease-out`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};
