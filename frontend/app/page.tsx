"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  MessageSquare,
  Search,
  GitCompare,
  BarChart3,
  ShieldAlert,
  Activity,
  Layers,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";

export default function HomePage() {
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => {
        setHealthStatus(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Health check error:", err);
        setHealthStatus({ status: "offline", error: String(err) });
        setLoading(false);
      });
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Strict Medical Disclaimer Header */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-xs text-amber-300 flex items-center justify-center gap-2">
        <ShieldAlert className="w-4 h-4 flex-shrink-0" />
        <span>
          <strong>EDUCATIONAL & RESEARCH USE ONLY:</strong> MedAssist AI does NOT diagnose conditions, prescribe medication, or provide personalized clinical treatment. Always consult licensed medical professionals.
        </span>
      </div>

      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Activity className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <span className="font-bold text-lg text-white tracking-tight">MedAssist</span>
              <span className="text-xs ml-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">AI Intelligence</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              {loading ? "Checking System..." : healthStatus?.status === "ok" ? "Core API Online" : "Connecting..."}
            </div>
            <Link
              href="/login"
              className="text-sm font-medium text-slate-300 hover:text-white transition px-3 py-1.5"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="text-sm font-medium bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-4 py-1.5 rounded-lg transition shadow-md shadow-emerald-500/20 font-semibold"
            >
              Launch Platform
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-12 flex flex-col justify-center">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/80 text-xs text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Hybrid RAG • LangGraph Agent Orchestration • MCP Tools</span>
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-white">
            Medical Document Intelligence & Knowledge Platform
          </h1>

          <p className="text-slate-400 text-lg leading-relaxed">
            Ingest clinical publications, lab guidelines, and healthcare records. Perform grounded semantic retrieval, verifiable citation extraction, and terminology decoding with non-diagnostic safety guardrails.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-6 py-3 rounded-xl font-bold transition shadow-lg shadow-emerald-500/25"
            >
              <span>Explore Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-xl font-medium border border-slate-700 transition"
            >
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <span>Ask AI (Grounded RAG)</span>
            </Link>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center border border-blue-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Document Ingestion & OCR</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Upload PDF, DOCX, TXT, and CSV documents with automatic text cleaning, page-tracking, metadata extraction, and OCR fallback.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Hybrid Retrieval & Citations</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Vector similarity combined with BM25 keyword search, score fusion reranking, and exact page/chunk level citation cards.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Agentic AI & MCP Architecture</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              LangGraph-directed multi-agent network (Query, Document, Knowledge, Analysis, Report) integrated with Model Context Protocol tools.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 bg-slate-950 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p>© 2026 MedAssist AI. Strictly for Medical Education and Document Intelligence.</p>
          <div className="flex gap-6">
            <Link href="/terms" className="hover:text-slate-400">Terms of Service</Link>
            <Link href="/privacy" className="hover:text-slate-400">Privacy Policy</Link>
            <Link href="/safety" className="hover:text-slate-400">Medical Safety Notice</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
