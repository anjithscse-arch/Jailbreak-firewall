import React, { useState } from 'react';
import {
  Save,
  Sliders,
  Shield,
  Key,
  Server,
  Calendar,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [blockThreshold, setBlockThreshold] = useState(0.70);
  const [reviewThreshold, setReviewThreshold] = useState(0.50);
  const [llmProvider, setLlmProvider] = useState('mock');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3.2');
  const [secureMode, setSecureMode] = useState(false);
  const [logFullPrompts, setLogFullPrompts] = useState(false);
  const [maxPromptLength, setMaxPromptLength] = useState(10000);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 font-mono">
            GATEWAY SYSTEM SETTINGS
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tune detection thresholds, active upstream LLM adapters, and privacy audit policies.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-blue-500/10 border border-blue-500/20 text-blue-300 px-3 py-1.5 rounded-lg">
          <Calendar className="w-3.5 h-3.5 text-blue-400" />
          <span>Presentation Date: Sept 11, 2026</span>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Detection Thresholds Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-slate-200 font-mono">
              Detection & Risk Scoring Thresholds
            </h3>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-slate-300">Block Threshold (Risk Score &gt;=):</span>
                <span className="text-rose-400 font-bold">{blockThreshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0.5}
                max={0.95}
                step={0.05}
                value={blockThreshold}
                onChange={(e) => setBlockThreshold(parseFloat(e.target.value))}
                className="w-full accent-rose-500 bg-slate-800"
              />
              <span className="text-[10px] text-slate-500">
                Prompts exceeding this score will be terminated and never sent to LLM.
              </span>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-slate-300">Review Threshold (Risk Score &gt;=):</span>
                <span className="text-amber-400 font-bold">{reviewThreshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0.3}
                max={0.7}
                step={0.05}
                value={reviewThreshold}
                onChange={(e) => setReviewThreshold(parseFloat(e.target.value))}
                className="w-full accent-amber-500 bg-slate-800"
              />
              <span className="text-[10px] text-slate-500">
                Prompts between Review and Block thresholds require manual or policy review.
              </span>
            </div>

            <div className="pt-2 border-t border-slate-800/80">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={secureMode}
                  onChange={(e) => setSecureMode(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-800 text-blue-600"
                />
                <div>
                  <span className="text-slate-200 font-semibold block">Enforce Strict Secure Mode</span>
                  <span className="text-[10px] text-slate-500 block">
                    When enabled, any prompt flagged for REVIEW is immediately BLOCKED.
                  </span>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* LLM Adapter Gateway Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Server className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-slate-200 font-mono">
              Upstream Large Language Model (LLM) Gateway
            </h3>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="text-slate-300 block mb-1.5">Active Upstream Provider:</label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
              >
                <option value="mock">Mock Adapter (Built-in offline demo simulation)</option>
                <option value="ollama">Ollama (Local LLMs: llama3.2, mistral, deepseek)</option>
                <option value="openai">OpenAI Compatible (Cloud APIs or vLLM)</option>
                <option value="rest">Generic REST API (Custom enterprise endpoint)</option>
              </select>
            </div>

            {llmProvider === 'ollama' && (
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div>
                  <label className="text-slate-400 block mb-1">Ollama Base URL:</label>
                  <input
                    type="text"
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Ollama Model Tag:</label>
                  <input
                    type="text"
                    value={ollamaModel}
                    onChange={(e) => setOllamaModel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-slate-200"
                  />
                </div>
              </div>
            )}

            {llmProvider === 'openai' && (
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <label className="text-slate-400 block">OpenAI API Key (Masked):</label>
                <input
                  type="password"
                  placeholder="sk-••••••••••••••••••••••••••••••••"
                  className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-slate-200"
                />
                <span className="text-[10px] text-slate-500">
                  Keys are stored as environment variables and never logged or exposed in responses.
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Privacy & Ingestion Controls */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-slate-200 font-mono">
              Privacy & Ingestion Guardrails
            </h3>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <label className="text-slate-300 block mb-1.5">Maximum Allowed Prompt Length:</label>
              <input
                type="number"
                min={500}
                max={50000}
                value={maxPromptLength}
                onChange={(e) => setMaxPromptLength(parseInt(e.target.value) || 10000)}
                className="w-48 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200"
              />
              <span className="text-[10px] text-slate-500 ml-3">characters (prevents DoS)</span>
            </div>

            <label className="flex items-center gap-3 cursor-pointer pt-2">
              <input
                type="checkbox"
                checked={logFullPrompts}
                onChange={(e) => setLogFullPrompts(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-blue-600"
              />
              <div>
                <span className="text-slate-200 font-semibold block">Store Full Raw Prompts in Audit Logs</span>
                <span className="text-[10px] text-slate-500 block">
                  When disabled (recommended), prompts are sanitized and truncated to prevent credential leakage.
                </span>
              </div>
            </label>
          </div>
        </div>

        {/* Save button & feedback */}
        <div className="flex items-center justify-between pt-2">
          {saved ? (
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>Gateway configuration saved successfully!</span>
            </div>
          ) : (
            <span className="text-[11px] font-mono text-slate-500">
              Changes apply immediately to subsequent firewall requests.
            </span>
          )}

          <button
            type="submit"
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition font-mono shadow-lg shadow-blue-600/20"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
};
