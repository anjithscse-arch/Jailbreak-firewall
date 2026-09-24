import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Play,
  CheckCircle2,
  AlertTriangle,
  Zap,
  TrendingUp,
  Clock,
  ShieldAlert,
  Cpu,
  Layers,
} from 'lucide-react';
import { metricsApi } from '../api/metricsApi';
import { EvaluationResult, LayerMetrics } from '../types/metrics';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

export const EvaluationPage: React.FC = () => {
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLatestEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await metricsApi.runEvaluation();
      setEvaluation(res);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load evaluation benchmark.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestEvaluation();
  }, []);

  const handleTriggerEvaluation = async () => {
    setRunning(true);
    try {
      const res = await metricsApi.runEvaluation();
      setEvaluation(res);
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Evaluation run failed.');
    } finally {
      setRunning(false);
    }
  };

  const renderMetricRow = (
    label: string,
    ruleVal: string | number,
    mlVal: string | number,
    combVal: string | number,
    highlightBest = false
  ) => (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-800/80 text-xs font-mono">
      <span className="text-slate-400">{label}</span>
      <div className="flex items-center gap-12 text-right">
        <span className="w-16 text-slate-300">{ruleVal}</span>
        <span className="w-16 text-slate-300">{mlVal}</span>
        <span
          className={`w-16 font-bold ${
            highlightBest ? 'text-emerald-400' : 'text-blue-400'
          }`}
        >
          {combVal}
        </span>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
            EMPIRICAL EVALUATION & BENCHMARKS
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Comparative performance analysis: Layer 1 (Deterministic Rules) vs. Layer 2 (ML Classifier) vs. Combined Hybrid Firewall.
          </p>
        </div>
        <button
          disabled={running}
          onClick={handleTriggerEvaluation}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white transition font-mono shadow-lg shadow-emerald-600/20 shrink-0 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5" />
          <span>{running ? 'Running Benchmark...' : 'Run Live Benchmark'}</span>
        </button>
      </div>

      {loading ? (
        <LoadingSpinner message="Calculating evaluation statistics across splits..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchLatestEvaluation} />
      ) : evaluation ? (
        <div className="space-y-8">
          {/* Top Comparative KPI Highlight */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Layer 1 Rule Only */}
            <div className="rounded-xl border border-indigo-500/30 bg-slate-900/60 p-5 backdrop-blur-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-wider text-indigo-400 font-semibold">
                  Layer 1: Rule Engine Only
                </span>
                <ShieldAlert className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-slate-100">
                {(evaluation.rule_only.accuracy * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400">
                F1 Score: {(evaluation.rule_only.f1 * 100).toFixed(1)}% | Latency:{' '}
                {evaluation.rule_only.avg_latency_ms} ms
              </p>
              <div className="text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                Ultra-low latency, high precision on known patterns.
              </div>
            </div>

            {/* Layer 2 ML Only */}
            <div className="rounded-xl border border-cyan-500/30 bg-slate-900/60 p-5 backdrop-blur-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">
                  Layer 2: ML Classifier Only
                </span>
                <Cpu className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-slate-100">
                {(evaluation.ml_only.accuracy * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-slate-400">
                F1 Score: {(evaluation.ml_only.f1 * 100).toFixed(1)}% | Latency:{' '}
                {evaluation.ml_only.avg_latency_ms} ms
              </p>
              <div className="text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800">
                High recall on semantic variations and obfuscation.
              </div>
            </div>

            {/* Combined Hybrid */}
            <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/20 p-5 backdrop-blur-sm space-y-3 relative overflow-hidden">
              <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-bold">
                  Two-Layer Hybrid Firewall
                </span>
                <Layers className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-3xl font-bold font-mono text-emerald-300">
                {(evaluation.combined.accuracy * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-emerald-200/80">
                F1 Score: {(evaluation.combined.f1 * 100).toFixed(1)}% | Latency:{' '}
                {evaluation.combined.avg_latency_ms} ms
              </p>
              <div className="text-[11px] font-mono text-emerald-400/90 pt-2 border-t border-emerald-500/20 font-semibold">
                ★ Best of both: Maximizes detection coverage and minimization of false negatives.
              </div>
            </div>
          </div>

          {/* Full Comparative Metrics Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <h3 className="text-sm font-semibold text-slate-200 font-mono">
                Comparative Performance Matrix (Evaluated on Test Split)
              </h3>
              <div className="flex items-center gap-12 text-xs font-mono text-slate-400 text-right">
                <span className="w-16">Rule Only</span>
                <span className="w-16">ML Only</span>
                <span className="w-16 text-emerald-400 font-bold">Combined</span>
              </div>
            </div>

            <div className="space-y-1">
              {renderMetricRow(
                'Detection Accuracy',
                `${(evaluation.rule_only.accuracy * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.accuracy * 100).toFixed(1)}%`,
                `${(evaluation.combined.accuracy * 100).toFixed(1)}%`,
                true
              )}
              {renderMetricRow(
                'Precision (Positive Predictive Value)',
                `${(evaluation.rule_only.precision * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.precision * 100).toFixed(1)}%`,
                `${(evaluation.combined.precision * 100).toFixed(1)}%`,
                true
              )}
              {renderMetricRow(
                'Recall (Sensitivity / Detection Rate)',
                `${(evaluation.rule_only.recall * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.recall * 100).toFixed(1)}%`,
                `${(evaluation.combined.recall * 100).toFixed(1)}%`,
                true
              )}
              {renderMetricRow(
                'F1-Score (Harmonic Mean)',
                `${(evaluation.rule_only.f1 * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.f1 * 100).toFixed(1)}%`,
                `${(evaluation.combined.f1 * 100).toFixed(1)}%`,
                true
              )}
              {renderMetricRow(
                'False Positive Rate (FPR)',
                `${(evaluation.rule_only.false_positive_rate * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.false_positive_rate * 100).toFixed(1)}%`,
                `${(evaluation.combined.false_positive_rate * 100).toFixed(1)}%`
              )}
              {renderMetricRow(
                'False Negative Rate (FNR)',
                `${(evaluation.rule_only.false_negative_rate * 100).toFixed(1)}%`,
                `${(evaluation.ml_only.false_negative_rate * 100).toFixed(1)}%`,
                `${(evaluation.combined.false_negative_rate * 100).toFixed(1)}%`,
                true
              )}
              {renderMetricRow(
                'Average Latency per Prompt',
                `${evaluation.rule_only.avg_latency_ms} ms`,
                `${evaluation.ml_only.avg_latency_ms} ms`,
                `${evaluation.combined.avg_latency_ms} ms`
              )}
              {renderMetricRow(
                '95th Percentile Latency (p95)',
                `${evaluation.rule_only.p95_latency_ms} ms`,
                `${evaluation.ml_only.p95_latency_ms} ms`,
                `${evaluation.combined.p95_latency_ms} ms`
              )}
            </div>
          </div>

          {/* Confusion Matrix Display */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
            <h3 className="text-sm font-semibold text-slate-200 font-mono">
              Confusion Matrix: Combined Firewall Pipeline
            </h3>
            <p className="text-xs text-slate-400">
              Evaluated across {evaluation.combined.total_evaluated} test samples.
            </p>

            <div className="grid grid-cols-2 max-w-md gap-3 text-center text-xs font-mono mx-auto pt-2">
              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-4">
                <span className="text-slate-400 block text-[10px] uppercase">True Negatives (TN)</span>
                <span className="text-2xl font-bold text-emerald-400 mt-1 block">
                  {evaluation.combined.true_negatives}
                </span>
                <span className="text-[10px] text-slate-500">Benign Allowed</span>
              </div>

              <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 p-4">
                <span className="text-slate-400 block text-[10px] uppercase">False Positives (FP)</span>
                <span className="text-2xl font-bold text-rose-400 mt-1 block">
                  {evaluation.combined.false_positives}
                </span>
                <span className="text-[10px] text-slate-500">Benign Blocked</span>
              </div>

              <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-4">
                <span className="text-slate-400 block text-[10px] uppercase">False Negatives (FN)</span>
                <span className="text-2xl font-bold text-amber-400 mt-1 block">
                  {evaluation.combined.false_negatives}
                </span>
                <span className="text-[10px] text-slate-500">Attacks Missed</span>
              </div>

              <div className="rounded-lg bg-blue-500/10 border border-blue-500/30 p-4">
                <span className="text-slate-400 block text-[10px] uppercase">True Positives (TP)</span>
                <span className="text-2xl font-bold text-blue-400 mt-1 block">
                  {evaluation.combined.true_positives}
                </span>
                <span className="text-[10px] text-slate-500">Attacks Blocked</span>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
