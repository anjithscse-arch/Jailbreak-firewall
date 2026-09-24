import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'blue' | 'emerald' | 'rose' | 'amber' | 'slate';
  trend?: string;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'blue',
  trend,
}) => {
  const variantStyles = {
    blue: {
      border: 'border-blue-500/20 hover:border-blue-500/40',
      iconBg: 'bg-blue-500/10 text-blue-400',
    },
    emerald: {
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400',
    },
    rose: {
      border: 'border-rose-500/20 hover:border-rose-500/40',
      iconBg: 'bg-rose-500/10 text-rose-400',
    },
    amber: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400',
    },
    slate: {
      border: 'border-slate-700/60 hover:border-slate-600',
      iconBg: 'bg-slate-800 text-slate-300',
    },
  };

  const style = variantStyles[variant];

  return (
    <div
      className={`rounded-xl bg-slate-900/60 border ${style.border} p-5 backdrop-blur-sm transition-all duration-200 glass-panel-hover flex flex-col justify-between`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={`p-2 rounded-lg ${style.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4">
        <div className="text-2xl font-bold font-mono text-slate-100">{value}</div>
        <div className="flex items-center justify-between mt-1 text-xs">
          {subtitle && <span className="text-slate-400">{subtitle}</span>}
          {trend && <span className="text-emerald-400 font-mono font-medium">{trend}</span>}
        </div>
      </div>
    </div>
  );
};
