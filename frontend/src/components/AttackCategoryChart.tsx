import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { CategoryDistribution } from '../types/metrics';

interface AttackCategoryChartProps {
  data: CategoryDistribution[];
}

const CATEGORY_COLORS: Record<string, string> = {
  BENIGN: '#10b981',
  DIRECT_PROMPT_INJECTION: '#ef4444',
  JAILBREAK: '#f43f5e',
  SYSTEM_PROMPT_LEAK: '#f59e0b',
  INDIRECT_PROMPT_INJECTION: '#8b5cf6',
  OBFUSCATED_ATTACK: '#ec4899',
  ROLE_MANIPULATION: '#06b6d4',
  DATA_EXFILTRATION: '#f97316',
  TOOL_MANIPULATION: '#e11d48',
  MULTI_TURN_MANIPULATION: '#6366f1',
};

export const AttackCategoryChart: React.FC<AttackCategoryChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs font-mono text-slate-500">
        No category distribution data recorded yet.
      </div>
    );
  }

  // Format category labels for display
  const chartData = data.map((d) => ({
    ...d,
    formattedCategory: d.category.replace(/_/g, ' ').toLowerCase(),
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
        >
          <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="formattedCategory"
            stroke="#94a3b8"
            width={120}
            tick={{ fontSize: 10, fill: '#cbd5e1' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#f8fafc',
            }}
            formatter={(value: any, name: any, item: any) => [
              `${value} requests (${item.payload.percentage}%)`,
              'Count',
            ]}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CATEGORY_COLORS[entry.category] || '#3b82f6'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
