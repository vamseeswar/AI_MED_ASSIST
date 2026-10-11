"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { getDocuments, sendChatMessage, DocumentItem } from "../../lib/api";
import {
  FileBarChart,
  FileText,
  Download,
  Sparkles,
  RefreshCw,
  Layers,
  Copy,
  Check,
  AlertCircle,
} from "lucide-react";

export default function ReportsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState("");
  const [reportType, setReportType] = useState<"summary" | "structured" | "findings">("summary");
  const [loading, setLoading] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getDocuments()
      .then((res) => {
        const docs = res.documents || [];
        setDocuments(docs);
        if (docs.length > 0) setSelectedDocId(docs[0].id);
      })
      .catch(() => {});
  }, []);

  async function handleGenerateReport(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedDocId) {
      setError("Please select a document to generate a report.");
      return;
    }

    setLoading(true);
    setError("");
    setGeneratedReport(null);

    const doc = documents.find((d) => d.id === selectedDocId);
    const docName = doc?.filename || "Medical Document";

    let instruction = "";
    if (reportType === "summary") {
      instruction = `Generate an Executive Clinical Summary Report for "${docName}". Structure it with Background, Key Findings, Methodology, and Summary Points. Ground in source text.`;
    } else if (reportType === "structured") {
      instruction = `Generate a Structured Information Extraction Report for "${docName}". Include tables or bullet lists of Demographics, Biomarkers, Vital Ranges, and Document Metadata. Ground in source text.`;
    } else {
      instruction = `Generate a Clinical Findings Analysis Report for "${docName}". Emphasize observational outcomes, statistical measures, and limitations noted in the document. Ground in source text.`;
    }

    try {
      const res = await sendChatMessage(instruction, undefined, selectedDocId);
      setGeneratedReport(res.answer);
    } catch (err: any) {
      setError(err.message || "Failed to generate report");
    } finally {
      setLoading(false);
    }
  }

  function handleDownloadMarkdown() {
    if (!generatedReport) return;
    const blob = new Blob([generatedReport], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `MedAssist_Report_${reportType}_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleCopy() {
    if (!generatedReport) return;
    navigator.clipboard.writeText(generatedReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-5xl mx-auto space-y-8 w-full">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Clinical Report Generator
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Synthesize structured clinical summaries, biomarker extractions, and observational reports grounded in your document repository.
            </p>
          </div>

          {/* Generator Controls */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-5 shadow-sm">
            <form onSubmit={handleGenerateReport} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
                    Source Document:
                  </label>
                  <select
                    value={selectedDocId}
                    onChange={(e) => setSelectedDocId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">Select Document</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.filename} ({d.file_type.toUpperCase()})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
                    Report Specification:
                  </label>
                  <select
                    value={reportType}
                    onChange={(e: any) => setReportType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="summary">Executive Clinical Summary</option>
                    <option value="structured">Structured Data & Biomarker Extraction</option>
                    <option value="findings">Clinical Findings & Limitations</option>
                  </select>
                </div>
              </div>

              {error && (
                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !selectedDocId}
                className="w-full py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/20"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <FileBarChart className="h-4 w-4" />}
                <span>{loading ? "Synthesizing Report..." : "Generate Report"}</span>
              </button>
            </form>
          </div>

          {/* Generated Report Display */}
          {generatedReport && (
            <div className="p-6 md:p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-5 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
                  <Sparkles className="h-5 w-5" />
                  <span>Generated Report</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition"
                  >
                    {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copied ? "Copied" : "Copy"}</span>
                  </button>
                  <button
                    onClick={handleDownloadMarkdown}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition shadow-sm"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>Download (.md)</span>
                  </button>
                </div>
              </div>

              <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/60 p-6 rounded-xl border border-slate-800 font-mono text-xs">
                {generatedReport}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
