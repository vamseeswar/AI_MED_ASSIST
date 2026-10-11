"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import {
  getSystemMetrics,
  getAuditLogs,
  getEvaluationResults,
  runEvaluationBenchmark,
  classifyDocumentML,
  classifyDocumentDL,
  SystemMetrics,
} from "../../lib/api";
import {
  Cpu,
  Activity,
  Layers,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  Clock,
  Terminal,
  Play,
  CheckCircle2,
  AlertCircle,
  Brain,
} from "lucide-react";

export default function AdminObservabilityPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [evalResults, setEvalResults] = useState<any | null>(null);
  const [runningEval, setRunningEval] = useState(false);
  const [loading, setLoading] = useState(true);

  // ML / DL test bench
  const [classifierText, setClassifierText] = useState(
    "PATIENT CLINICAL SUMMARY: Patient presented with stage 2 hypertension. Blood pressure measured at 145/95 mmHg. Diagnostic electrocardiogram demonstrated normal sinus rhythm without ischemic changes."
  );
  const [mlResult, setMlResult] = useState<any | null>(null);
  const [dlResult, setDlResult] = useState<any | null>(null);
  const [classifying, setClassifying] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [m, logsRes, evalRes] = await Promise.all([
        getSystemMetrics().catch(() => null),
        getAuditLogs(20).catch(() => ({ total: 0, items: [] })),
        getEvaluationResults().catch(() => null),
      ]);
      setMetrics(m);
      setAuditLogs(logsRes.items || []);
      setTotalLogs(logsRes.total || 0);
      setEvalResults(evalRes);
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunEvaluation() {
    setRunningEval(true);
    try {
      const res = await runEvaluationBenchmark();
      setEvalResults(res);
    } catch (err) {
      console.error("Evaluation execution failed:", err);
    } finally {
      setRunningEval(false);
    }
  }

  async function handleRunClassification() {
    if (!classifierText.trim()) return;
    setClassifying(true);
    setMlResult(null);
    setDlResult(null);
    try {
      const [ml, dl] = await Promise.all([
        classifyDocumentML(classifierText).catch((err) => ({ error: err.message })),
        classifyDocumentDL(classifierText).catch((err) => ({ error: err.message })),
      ]);
      setMlResult(ml);
      setDlResult(dl);
    } catch (err) {
      console.error("Classification error:", err);
    } finally {
      setClassifying(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto space-y-8 w-full">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              System Observability & AI Telemetry
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Live audit logs, real-time RAG evaluation metrics, ML/DL classification diagnostics, and platform security telemetry.
            </p>
          </div>

          {/* Section 1: Live System Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { label: "Active Users", val: metrics?.counts.users ?? 0 },
              { label: "Total Docs", val: metrics?.counts.documents ?? 0 },
              { label: "Vector Chunks", val: metrics?.counts.chunks ?? 0 },
              { label: "Conversations", val: metrics?.counts.conversations ?? 0 },
              { label: "Chat Messages", val: metrics?.counts.messages ?? 0 },
              { label: "Audit Events", val: metrics?.counts.audit_logs ?? totalLogs },
            ].map((item, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-center">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  {item.label}
                </span>
                <span className="text-xl font-black text-cyan-400 mt-1 block">
                  {loading ? "..." : item.val}
                </span>
              </div>
            ))}
          </div>

          {/* Section 2: AI Evaluation Benchmark (Phase 19) */}
          <div className="p-6 md:p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                  <Brain className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white">
                    RAG Quality & Faithfulness Evaluation Benchmark
                  </h2>
                  <p className="text-xs text-slate-400">
                    Non-fabricated empirical benchmarks evaluating retrieval accuracy, groundedness, and citation fidelity.
                  </p>
                </div>
              </div>
              <button
                onClick={handleRunEvaluation}
                disabled={runningEval}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-bold transition shadow-lg shadow-purple-600/20"
              >
                {runningEval ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                <span>{runningEval ? "Evaluating Pipeline..." : "Run Evaluation Benchmark"}</span>
              </button>
            </div>

            {!evalResults || !evalResults.evaluated ? (
              <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-800/80 text-center text-xs text-slate-400 space-y-2">
                <span className="font-semibold text-slate-300 block">Not evaluated yet.</span>
                <p>Click &ldquo;Run Evaluation Benchmark&rdquo; to execute the test suite across medical query sets.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    {
                      label: "Hit Rate @ 3",
                      val: `${((evalResults.aggregate_metrics?.hit_rate_at_3 ?? 0) * 100).toFixed(1)}%`,
                      color: "text-emerald-400",
                    },
                    {
                      label: "Groundedness (Faithfulness)",
                      val: `${((evalResults.aggregate_metrics?.mean_groundedness ?? 0) * 100).toFixed(1)}%`,
                      color: "text-cyan-400",
                    },
                    {
                      label: "Citation Correctness",
                      val: `${((evalResults.aggregate_metrics?.mean_citation_correctness ?? 0) * 100).toFixed(1)}%`,
                      color: "text-blue-400",
                    },
                    {
                      label: "Avg Latency",
                      val: `${evalResults.aggregate_metrics?.avg_latency_ms ?? 0} ms`,
                      color: "text-purple-400",
                    },
                  ].map((stat, i) => (
                    <div key={i} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                        {stat.label}
                      </span>
                      <span className={`text-xl font-black mt-1 block ${stat.color}`}>
                        {stat.val}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between px-1">
                  <span>Last Evaluated: {new Date(evalResults.timestamp).toLocaleString()}</span>
                  <span>Total Tokens: {evalResults.aggregate_metrics?.total_tokens_consumed} tokens</span>
                </div>
              </div>
            )}
          </div>

          {/* Section 3: ML / DL Classification Test Bench (Phase 14 & 15) */}
          <div className="p-6 md:p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-6 shadow-sm">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                <Cpu className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">
                  Safe Medical Document Classification (ML & DL)
                </h2>
                <p className="text-xs text-slate-400">
                  Non-diagnostic document categorization comparing Scikit-Learn TF-IDF vs PyTorch Transformer model.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <textarea
                value={classifierText}
                onChange={(e) => setClassifierText(e.target.value)}
                rows={3}
                placeholder="Enter sample medical report text..."
                className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
              />
              <button
                onClick={handleRunClassification}
                disabled={classifying || !classifierText.trim()}
                className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold text-xs transition flex items-center gap-2 shadow-md shadow-cyan-600/20"
              >
                {classifying ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                <span>{classifying ? "Classifying..." : "Run ML & DL Classification"}</span>
              </button>
            </div>

            {(mlResult || dlResult) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* ML Result */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-cyan-400">Scikit-Learn Classifier</span>
                    <span className="text-[10px] text-slate-400">v{mlResult?.model_version || "1.0"}</span>
                  </div>
                  {mlResult?.error ? (
                    <span className="text-xs text-red-400">{mlResult.error}</span>
                  ) : (
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Category:</span>
                        <span className="font-bold text-white uppercase">{mlResult?.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Confidence:</span>
                        <span className="font-bold text-emerald-400">
                          {((mlResult?.confidence || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Inference Latency:</span>
                        <span className="text-slate-300">{mlResult?.inference_time_ms} ms</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* DL Result */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-purple-400">PyTorch Transformer (DL)</span>
                    <span className="text-[10px] text-slate-400">v{dlResult?.model_version || "1.0"}</span>
                  </div>
                  {dlResult?.error ? (
                    <span className="text-xs text-red-400">{dlResult.error}</span>
                  ) : (
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Label:</span>
                        <span className="font-bold text-white uppercase">{dlResult?.label}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Confidence:</span>
                        <span className="font-bold text-emerald-400">
                          {((dlResult?.confidence || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Inference Latency:</span>
                        <span className="text-slate-300">{dlResult?.inference_time_ms} ms</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Section 4: Live Audit Logs */}
          <div className="p-6 md:p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="h-4 w-4 text-cyan-400" />
                <h2 className="text-base font-bold text-white">System Audit Trail ({totalLogs})</h2>
              </div>
              <span className="text-xs text-slate-400">Sensitive credentials masked</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
                  <tr>
                    <th className="py-2.5 px-3 rounded-l-lg">Timestamp</th>
                    <th className="py-2.5 px-3">Action</th>
                    <th className="py-2.5 px-3">Resource</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 rounded-r-lg">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">
                        {log.created_at ? new Date(log.created_at).toLocaleTimeString() : "-"}
                      </td>
                      <td className="py-2 px-3 font-bold text-white">{log.action}</td>
                      <td className="py-2 px-3 text-slate-400">
                        {log.resource_type ? `${log.resource_type}` : "-"}
                      </td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            log.status === "SUCCESS"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-red-500/10 text-red-400"
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-slate-400 truncate max-w-[200px] font-mono text-[11px]">
                        {log.details || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
