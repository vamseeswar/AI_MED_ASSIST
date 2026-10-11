"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import {
  getSystemMetrics,
  getDocuments,
  getConversations,
  DocumentItem,
  ConversationItem,
  SystemMetrics,
} from "../../lib/api";
import {
  FileText,
  MessageSquare,
  Activity,
  Layers,
  Upload,
  ArrowRight,
  ShieldCheck,
  Clock,
  Sparkles,
} from "lucide-react";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [recentDocs, setRecentDocs] = useState<DocumentItem[]>([]);
  const [recentConvos, setRecentConvos] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, docsRes, convos] = await Promise.all([
          getSystemMetrics().catch(() => null),
          getDocuments().catch(() => ({ total: 0, documents: [] })),
          getConversations().catch(() => []),
        ]);
        setMetrics(m);
        setRecentDocs(docsRes.documents.slice(0, 5));
        setRecentConvos(convos.slice(0, 5));
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto space-y-8 w-full">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                Medical Intelligence Dashboard
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Real-time source-grounded document analysis, RAG retrieval & system telemetry.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/documents"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium transition shadow-lg shadow-cyan-600/20"
              >
                <Upload className="h-4 w-4" />
                <span>Upload Document</span>
              </Link>
              <Link
                href="/chat"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition border border-slate-700"
              >
                <MessageSquare className="h-4 w-4 text-cyan-400" />
                <span>New AI Chat</span>
              </Link>
            </div>
          </div>

          {/* Metric Cards (All live from API) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Documents</span>
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                  <FileText className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-white">
                  {loading ? "..." : metrics?.counts.documents ?? recentDocs.length}
                </div>
                <div className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5 text-cyan-400" />
                  <span>{metrics?.counts.chunks ?? 0} indexed chunks</span>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Conversations</span>
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                  <MessageSquare className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-white">
                  {loading ? "..." : metrics?.counts.conversations ?? recentConvos.length}
                </div>
                <div className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-blue-400" />
                  <span>{metrics?.counts.messages ?? 0} total messages</span>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Processing Jobs</span>
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <Activity className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-white">
                  {loading ? "..." : (metrics?.job_status_breakdown?.COMPLETED ?? 0) + (metrics?.job_status_breakdown?.PROCESSING ?? 0)}
                </div>
                <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>{metrics?.job_status_breakdown?.COMPLETED ?? 0} completed safely</span>
                </div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">RAG Queries</span>
                <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                  <Sparkles className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-white">
                  {loading ? "..." : metrics?.audit_action_breakdown?.RAG_QUERY ?? metrics?.counts.messages ?? 0}
                </div>
                <div className="text-xs text-purple-300 mt-1 flex items-center gap-1.5">
                  <span>Hybrid RRF & Re-ranked</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity Sections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Documents */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-cyan-400" />
                  <h2 className="text-base font-bold text-white">Recent Documents</h2>
                </div>
                <Link
                  href="/documents"
                  className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                >
                  <span>View All</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {recentDocs.length === 0 ? (
                <div className="py-8 text-center text-sm text-slate-500">
                  No documents uploaded yet. Upload a PDF, DOCX, TXT, or CSV to begin.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {recentDocs.map((doc) => (
                    <Link
                      key={doc.id}
                      href={`/documents/${doc.id}`}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:border-cyan-500/40 flex items-center justify-between transition group"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500/20 transition">
                          <FileText className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-slate-200 group-hover:text-cyan-300 transition truncate max-w-[220px]">
                            {doc.filename}
                          </div>
                          <div className="text-xs text-slate-400">
                            {doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB • {doc.page_count} pages
                          </div>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {doc.status}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Conversations */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-blue-400" />
                  <h2 className="text-base font-bold text-white">Recent Conversations</h2>
                </div>
                <Link
                  href="/chat"
                  className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                >
                  <span>Open Chat</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              {recentConvos.length === 0 ? (
                <div className="py-8 text-center text-sm text-slate-500">
                  No active chat sessions. Start a conversation with MedAssist AI.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {recentConvos.map((convo) => (
                    <Link
                      key={convo.id}
                      href={`/chat?id=${convo.id}`}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:border-blue-500/40 flex items-center justify-between transition group"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition">
                          <MessageSquare className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-slate-200 group-hover:text-blue-300 transition truncate max-w-[240px]">
                            {convo.title || "Medical Query"}
                          </div>
                          <div className="text-xs text-slate-400 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            <span>{new Date(convo.updated_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-slate-300 transition" />
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
