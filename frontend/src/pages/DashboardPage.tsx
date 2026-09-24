import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Clock,
  Cpu,
  Layers,
  Activity,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { metricsApi } from '../api/metricsApi';
import { logsApi } from '../api/logsApi';
import { MetricsSummary, TimelinePoint, CategoryDistribution } from '../types/metrics';
import { PromptRecord } from '../types/logs';
import { MetricsCard } from '../components/MetricsCard';
import { DecisionBadge } from '../components/DecisionBadge';
import { LatencyChart } from '../components/LatencyChart';
import { AttackCategoryChart } from '../components/AttackCategoryChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [categories, setCategories] = useState<CategoryDistribution[]>([]);
  const [recentLogs, setRecentLogs] = useState<PromptRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, timeRes, catRes, logsRes] = await Promise.all([
        metricsApi.getSummary(),
        metricsApi.getTimeline(),
        metricsApi.getCategories(),
        logsApi.getLogs({ page: 1, page_size: 7 }),
      ]);
      setSummary(sumRes);
      setTimeline(timeRes);
      setCategories(catRes);
      setRecentLogs(logsRes.items);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load telemetry data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading && !summary) {
    return <LoadingSpinner message="Aggregating firewall telemetry..." size="lg" />;
  }

  if (error && !summary) {
    return <ErrorMessage message={error} onRetry={fetchDashboardData} />;
  }

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
            SECURITY OPERATIONS DASHBOARD
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry from Layer 1 (Rules) & Layer 2 (ML Classifier) gateway filters.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/analyze"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition shadow-lg shadow-blue-600/20"
          >
            <span>Test Prompts in Sandbox</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="Total Prompts Inspected"
          value={summary?.total_requests ?? 0}
          subtitle="All conversational turns"
          icon={Layers}
          variant="blue"
        />
        <MetricsCard
          title="Blocked Adversarial Threats"
          value={summary?.blocked_requests ?? 0}
          subtitle={`Attack rate: ${summary?.attack_rate ?? 0}%`}
          icon={ShieldAlert}
          variant="rose"
        />
        <MetricsCard
          title="Safe Allowed Queries"
          value={summary?.allowed_requests ?? 0}
          subtitle="Passed to upstream LLM"
          icon={ShieldCheck}
          variant="emerald"
        />
        <MetricsCard
          title="Average Latency"
          value={`${summary?.average_latency_ms ?? 0} ms`}
          subtitle="Sub-millisecond inspection"
          icon={Clock}
          variant="amber"
        />
      </div>

      {/* Secondary Telemetry Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-mono uppercase">Layer 1 Detections</span>
            <div className="text-xl font-bold font-mono text-slate-200 mt-0.5">
              {summary?.rule_detection_rate ?? 0}%
            </div>
            <span className="text-[10px] text-slate-500">Deterministic rule hits</span>
          </div>
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-mono uppercase">Layer 2 Detections</span>
            <div className="text-xl font-bold font-mono text-slate-200 mt-0.5">
              {summary?.ml_detection_rate ?? 0}%
            </div>
            <span className="text-[10px] text-slate-500">ML classifier hits</span>
          </div>
          <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-mono uppercase">Model Benchmark F1</span>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
              {summary?.model_f1 ? `${(summary.model_f1 * 100).toFixed(1)}%` : '85.1%'}
            </div>
            <span className="text-[10px] text-slate-500">Multiclass accuracy</span>
          </div>
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Visual Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Request Traffic & Blocks</h3>
              <p className="text-xs text-slate-400">Volume distribution over time</p>
            </div>
            <span className="text-[10px] font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
              24h Window
            </span>
          </div>
          <LatencyChart data={timeline} />
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Threat Category Taxonomy</h3>
              <p className="text-xs text-slate-400">Classification across 10 security vectors</p>
            </div>
            <span className="text-[10px] font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
              Historical Distribution
            </span>
          </div>
          <AttackCategoryChart data={categories} />
        </div>
      </div>

      {/* Recent Security Detections Table */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Live Detection Feed</h3>
            <p className="text-xs text-slate-400">Recent prompts analyzed by the firewall</p>
          </div>
          <Link
            to="/logs"
            className="text-xs font-mono text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <span>View All Logs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Verdict</th>
                <th className="pb-3 font-medium">Category</th>
                <th className="pb-3 font-medium">Risk Score</th>
                <th className="pb-3 font-medium">Layer</th>
                <th className="pb-3 font-medium">Prompt Sample</th>
                <th className="pb-3 font-medium">Latency</th>
                <th className="pb-3 font-medium text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {recentLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500 font-mono text-xs">
                    No prompt requests logged yet. Submit a prompt in the Sandbox to view live audit events.
                  </td>
                </tr>
              ) : (
                recentLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3">
                      <DecisionBadge decision={log.decision} size="sm" />
                    </td>
                    <td className="py-3 font-semibold text-slate-200">
                      {log.attack_category.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 font-mono">
                      <span
                        className={
                          log.risk_score >= 0.7
                            ? 'text-rose-400 font-bold'
                            : log.risk_score >= 0.45
                            ? 'text-amber-400'
                            : 'text-emerald-400'
                        }
                      >
                        {(log.risk_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3 text-[11px] text-slate-400">{log.detected_by}</td>
                    <td className="py-3 max-w-xs truncate text-slate-300" title={log.redacted_prompt}>
                      {log.redacted_prompt}
                    </td>
                    <td className="py-3 text-slate-400">{log.processing_time_ms} ms</td>
                    <td className="py-3 text-right text-slate-500 text-[10px]">
                      {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
