"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { CitationCard } from "../../components/CitationCard";
import { getDocuments, sendChatMessage, DocumentItem } from "../../lib/api";
import {
  GitCompare,
  FileText,
  Sparkles,
  ArrowRight,
  RefreshCw,
  Layers,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

export default function ComparePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [docAId, setDocAId] = useState("");
  const [docBId, setDocBId] = useState("");
  const [loading, setLoading] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<string | null>(null);
  const [citations, setCitations] = useState<any[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getDocuments()
      .then((res) => {
        const docs = res.documents || [];
        setDocuments(docs);
        if (docs.length >= 2) {
          setDocAId(docs[0].id);
          setDocBId(docs[1].id);
        } else if (docs.length === 1) {
          setDocAId(docs[0].id);
        }
      })
      .catch(() => {});
  }, []);

  async function handleCompare(e: React.FormEvent) {
    e.preventDefault();
    if (!docAId || !docBId || docAId === docBId) {
      setError("Please select two distinct documents to compare.");
      return;
    }

    setLoading(true);
    setError("");
    setComparisonResult(null);
    setCitations([]);

    const docA = documents.find((d) => d.id === docAId)?.filename || "Document A";
    const docB = documents.find((d) => d.id === docBId)?.filename || "Document B";

    const prompt = (
      `Perform a comprehensive comparative analysis between "${docA}" (Document A) and "${docB}" (Document B).\n` +
      `Identify and structure:\n` +
      `1. Core Clinical & Research Similarities\n` +
      `2. Key Methodological or Result Differences\n` +
      `3. Changed / Conflicting Sections or Findings\n` +
      `4. Added or Unique Points in each document\n` +
      `Ground all points strictly in the provided document contexts and cite both sources.`
    );

    try {
      const res = await sendChatMessage(prompt, undefined, docAId);
      setComparisonResult(res.answer);
      setCitations(res.citations || []);
    } catch (err: any) {
      setError(err.message || "Failed to generate document comparison");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-6xl mx-auto space-y-8 w-full">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Document Comparison Engine
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Side-by-side analysis of clinical records, protocols, and medical research papers with verifiable citations from both sources.
            </p>
          </div>

          {/* Selection Card */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-6 shadow-sm">
            <form onSubmit={handleCompare} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Document A */}
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="h-4 w-4" />
                    <span>Reference Document A</span>
                  </span>
                  <select
                    value={docAId}
                    onChange={(e) => setDocAId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">Select Document A</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id} disabled={d.id === docBId}>
                        {d.filename} ({d.file_type.toUpperCase()})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Document B */}
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="h-4 w-4" />
                    <span>Comparison Document B</span>
                  </span>
                  <select
                    value={docBId}
                    onChange={(e) => setDocBId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Select Document B</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id} disabled={d.id === docAId}>
                        {d.filename} ({d.file_type.toUpperCase()})
                      </option>
                    ))}
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
                disabled={loading || !docAId || !docBId || docAId === docBId}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 disabled:opacity-50 text-white font-bold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/20"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <GitCompare className="h-4 w-4" />}
                <span>{loading ? "Synthesizing Comparison..." : "Run Side-by-Side Comparison"}</span>
              </button>
            </form>
          </div>

          {/* Comparison Output */}
          {comparisonResult && (
            <div className="p-6 md:p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-6 shadow-sm">
              <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
                <Sparkles className="h-5 w-5" />
                <span>Comparative Findings & Synthesis</span>
              </div>

              <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed whitespace-pre-wrap bg-slate-950/60 p-6 rounded-xl border border-slate-800">
                {comparisonResult}
              </div>

              {citations.length > 0 && (
                <div className="space-y-3 pt-4 border-t border-slate-800">
                  <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1.5">
                    <Layers className="h-3.5 w-3.5" />
                    <span>Dual-Source Citations:</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {citations.map((c, idx) => (
                      <CitationCard key={idx} citation={c} index={idx + 1} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
