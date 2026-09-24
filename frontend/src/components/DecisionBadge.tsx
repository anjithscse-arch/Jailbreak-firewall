import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

interface DecisionBadgeProps {
  decision: 'ALLOW' | 'BLOCK' | 'REVIEW';
  size?: 'sm' | 'md' | 'lg';
}

export const DecisionBadge: React.FC<DecisionBadgeProps> = ({ decision, size = 'md' }) => {
  const configs = {
    ALLOW: {
      bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 badge-glow-allow',
      icon: ShieldCheck,
      label: 'ALLOW',
      description: 'Passed Security Filters',
    },
    BLOCK: {
      bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400 badge-glow-block',
      icon: ShieldAlert,
      label: 'BLOCK',
      description: 'Hostile Threat Blocked',
    },
    REVIEW: {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400 badge-glow-review',
      icon: AlertTriangle,
      label: 'REVIEW',
      description: 'Requires Inspection',
    },
  };

  const config = configs[decision] || configs.REVIEW;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
    lg: 'px-4 py-2 text-base font-semibold gap-2',
  };

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-full border ${config.bg} ${sizeClasses[size]}`}
    >
      <Icon className={size === 'lg' ? 'w-5 h-5' : size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      <span>{config.label}</span>
    </span>
  );
};
