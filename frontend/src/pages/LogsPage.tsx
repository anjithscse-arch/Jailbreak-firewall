import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  Eye,
  Trash2,
  X,
  FileText,
} from 'lucide-react';
import { logsApi } from '../api/logsApi';
import { PromptRecord, LogDetail } from '../types/logs';
import { DecisionBadge } from '../components/DecisionBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

export const LogsPage: React.FC = () => {
  const [logs, setLogs] = useState<PromptRecord[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(15);

  // Filters
  const [search, setSearch] = useState('');
  const [decisionFilter, setDecisionFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [layerFilter, setLayerFilter] = useState('');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Detail Modal
  const [selectedLog, setSelectedLog] = useState<LogDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await logsApi.getLogs({
        page: currentPage,
        page_size: pageSize,
        decision: decisionFilter || undefined,
        category: categoryFilter || undefined,
        detected_by: layerFilter || undefined,
        search: search.trim() || undefined,
      });
      setLogs(res.items);
      setTotalCount(res.pagination.total_count);
      setTotalPages(res.pagination.total_pages);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to retrieve logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [currentPage, decisionFilter, categoryFilter, layerFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchLogs();
  };

  const handleViewDetail = async (requestId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await logsApi.getLogDetail(requestId);
      setSelectedLog(detail);
    } catch (err) {
      alert('Could not retrieve log details.');
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCopyId = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleExportCSV = () => {
    if (logs.length === 0) return;
    const headers = ['RequestID', 'Decision', 'Category', 'RiskScore', 'Layer', 'LatencyMS', 'Timestamp', 'Prompt'];
    const rows = logs.map((l) => [
      l.request_id,
      l.decision,
      l.attack_category,
      l.risk_score,
      l.detected_by,
      l.processing_time_ms,
      l.created_at,
      `"${l.redacted_prompt.replace(/"/g, '""')}"`,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `firewall_audit_logs_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
            SECURITY AUDIT LOGS
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Immutable audit record of all prompt evaluation requests and security enforcement events.
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 transition shrink-0"
        >
          <Download className="w-4 h-4 text-blue-400" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search prompt content or keywords..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition font-mono shrink-0"
          >
            Filter
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 pt-2 text-xs font-mono">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={decisionFilter}
            onChange={(e) => {
              setDecisionFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-300"
          >
            <option value="">All Decisions</option>
            <option value="ALLOW">ALLOW</option>
            <option value="BLOCK">BLOCK</option>
            <option value="REVIEW">REVIEW</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-300"
          >
            <option value="">All Categories</option>
            <option value="BENIGN">BENIGN</option>
            <option value="DIRECT_PROMPT_INJECTION">DIRECT PROMPT INJECTION</option>
            <option value="JAILBREAK">JAILBREAK</option>
            <option value="SYSTEM_PROMPT_LEAK">SYSTEM PROMPT LEAK</option>
            <option value="INDIRECT_PROMPT_INJECTION">INDIRECT INJECTION</option>
            <option value="OBFUSCATED_ATTACK">OBFUSCATED ATTACK</option>
            <option value="ROLE_MANIPULATION">ROLE MANIPULATION</option>
            <option value="DATA_EXFILTRATION">DATA EXFILTRATION</option>
            <option value="TOOL_MANIPULATION">TOOL MANIPULATION</option>
            <option value="MULTI_TURN_MANIPULATION">MULTI TURN MANIPULATION</option>
          </select>

          <select
            value={layerFilter}
            onChange={(e) => {
              setLayerFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-300"
          >
            <option value="">All Layers</option>
            <option value="RULE_ENGINE">RULE ENGINE</option>
            <option value="ML_CLASSIFIER">ML CLASSIFIER</option>
            <option value="BOTH">BOTH LAYERS</option>
            <option value="NONE">NONE</option>
          </select>

          {(decisionFilter || categoryFilter || layerFilter || search) && (
            <button
              onClick={() => {
                setDecisionFilter('');
                setCategoryFilter('');
                setLayerFilter('');
                setSearch('');
                setCurrentPage(1);
              }}
              className="text-rose-400 hover:text-rose-300 text-[11px] underline"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Querying audit records..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchLogs} />
      ) : (
        /* Logs Table */
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="p-3.5 font-medium">Verdict</th>
                  <th className="p-3.5 font-medium">Category</th>
                  <th className="p-3.5 font-medium">Risk</th>
                  <th className="p-3.5 font-medium">Layer</th>
                  <th className="p-3.5 font-medium">Prompt Preview</th>
                  <th className="p-3.5 font-medium">Latency</th>
                  <th className="p-3.5 font-medium">Time</th>
                  <th className="p-3.5 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-slate-500 font-mono">
                      No audit records matching specified filters.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition">
                      <td className="p-3.5">
                        <DecisionBadge decision={log.decision} size="sm" />
                      </td>
                      <td className="p-3.5 font-semibold text-slate-200">
                        {log.attack_category.replace(/_/g, ' ')}
                      </td>
                      <td className="p-3.5">
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
                      <td className="p-3.5 text-slate-400 text-[11px]">{log.detected_by}</td>
                      <td className="p-3.5 max-w-sm truncate text-slate-300" title={log.redacted_prompt}>
                        {log.redacted_prompt}
                      </td>
                      <td className="p-3.5 text-slate-400">{log.processing_time_ms} ms</td>
                      <td className="p-3.5 text-slate-500 text-[11px]">
                        {new Date(log.created_at).toLocaleTimeString()}
                      </td>
                      <td className="p-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleCopyId(log.request_id)}
                            title="Copy Request ID"
                            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
                          >
                            {copiedId === log.request_id ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                          <button
                            onClick={() => handleViewDetail(log.request_id)}
                            title="Inspect Details"
                            className="p-1 rounded hover:bg-blue-600/20 text-slate-400 hover:text-blue-400 transition"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
            <span>
              Showing {logs.length} of {totalCount} total audit records
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded border border-slate-800 bg-slate-950 disabled:opacity-30 hover:bg-slate-800 transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className="p-1.5 rounded border border-slate-800 bg-slate-950 disabled:opacity-30 hover:bg-slate-800 transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="w-full max-w-2xl rounded-xl border border-slate-800 bg-slate-900 p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <DecisionBadge decision={selectedLog.decision} size="sm" />
                <span className="text-sm font-bold font-mono text-slate-100">
                  Request: {selectedLog.request_id}
                </span>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div>
                <span className="text-slate-400 block mb-1">Sanitized Prompt:</span>
                <div className="rounded-lg bg-slate-950 border border-slate-800 p-3 text-slate-200 max-h-36 overflow-y-auto">
                  {selectedLog.redacted_prompt}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-slate-950 border border-slate-800 p-2.5">
                  <span className="text-slate-500">Threat Category:</span>
                  <div className="text-slate-200 font-semibold mt-0.5">{selectedLog.attack_category}</div>
                </div>
                <div className="rounded-lg bg-slate-950 border border-slate-800 p-2.5">
                  <span className="text-slate-500">Composite Risk Score:</span>
                  <div className="text-slate-200 font-semibold mt-0.5">
                    {(selectedLog.risk_score * 100).toFixed(1)}% (Confidence: {(selectedLog.confidence * 100).toFixed(1)}%)
                  </div>
                </div>
                <div className="rounded-lg bg-slate-950 border border-slate-800 p-2.5">
                  <span className="text-slate-500">Detection Layer:</span>
                  <div className="text-slate-200 font-semibold mt-0.5">{selectedLog.detected_by}</div>
                </div>
                <div className="rounded-lg bg-slate-950 border border-slate-800 p-2.5">
                  <span className="text-slate-500">Firewall Latency:</span>
                  <div className="text-slate-200 font-semibold mt-0.5">{selectedLog.processing_time_ms} ms</div>
                </div>
              </div>

              {/* Upstream LLM Response */}
              {selectedLog.llm_called && selectedLog.llm_response && (
                <div>
                  <span className="text-emerald-400 font-semibold block mb-1">
                    Upstream LLM Response ({selectedLog.llm_provider || 'Mock'}):
                  </span>
                  <div className="rounded-lg bg-slate-950 border border-emerald-500/20 p-3 text-slate-200 max-h-36 overflow-y-auto">
                    {selectedLog.llm_response}
                  </div>
                </div>
              )}

              {/* Linked Detection Events */}
              <div>
                <span className="text-slate-400 block mb-1">Security Events ({selectedLog.events.length}):</span>
                {selectedLog.events.length === 0 ? (
                  <p className="text-slate-500 italic">No specific rule violations logged.</p>
                ) : (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {selectedLog.events.map((ev) => (
                      <div
                        key={ev.id}
                        className="rounded bg-slate-950 border border-slate-800 p-2.5 flex items-start justify-between gap-2"
                      >
                        <div>
                          <span className="font-semibold text-slate-200 block">{ev.reason}</span>
                          <span className="text-slate-500 text-[10px]">
                            Layer: {ev.detection_layer} | Rule: {ev.rule_id || 'N/A'}
                          </span>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-rose-500/10 border border-rose-500/20 text-rose-300">
                          {ev.severity}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="border-t border-slate-800 pt-3 flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
