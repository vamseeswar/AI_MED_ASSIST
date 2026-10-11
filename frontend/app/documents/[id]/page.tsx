"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Navbar } from "../../../components/Navbar";
import { Sidebar } from "../../../components/Sidebar";
import { DisclaimerBanner } from "../../../components/DisclaimerBanner";
import { getDocumentById, DocumentItem } from "../../../lib/api";
import {
  FileText,
  MessageSquare,
  ArrowLeft,
  Calendar,
  Layers,
  CheckCircle,
  Clock,
  Sparkles,
  Info,
  BookOpen,
} from "lucide-react";

export default function DocumentDetailPage() {
  const params = useParams();
  const docId = params.id as string;

  const [document, setDocument] = useState<(DocumentItem & { chunks?: any[] }) | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDoc() {
      try {
        setLoading(true);
        const data = await getDocumentById(docId);
        setDocument(data);
      } catch (err: any) {
        setError(err.message || "Failed to load document");
      } finally {
        setLoading(false);
      }
    }
    if (docId) loadDoc();
  }, [docId]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-5xl mx-auto space-y-6 w-full">
          {/* Back button */}
          <Link
            href="/documents"
            className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-cyan-400 transition w-fit"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to All Documents</span>
          </Link>

          {loading ? (
            <div className="py-20 text-center text-slate-400 flex items-center justify-center gap-2">
              <Clock className="h-5 w-5 animate-spin text-cyan-400" />
              <span>Loading document analysis...</span>
            </div>
          ) : error || !document ? (
            <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400">
              {error || "Document not found"}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Header Card */}
              <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-sm">
                <div className="flex items-start gap-4">
                  <div className="p-3.5 rounded-2xl bg-cyan-500/10 text-cyan-400">
                    <FileText className="h-8 w-8" />
                  </div>
                  <div>
                    <h1 className="text-xl md:text-2xl font-black text-white">
                      {document.filename}
                    </h1>
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase font-bold text-[10px]">
                        {document.file_type}
                      </span>
                      <span>{(document.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span>{document.page_count} Pages</span>
                      <span>•</span>
                      <span>{document.word_count} Words</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{new Date(document.created_at).toLocaleDateString()}</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Primary CTA */}
                <Link
                  href={`/chat?docId=${document.id}`}
                  className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition shadow-lg shadow-cyan-600/20 shrink-0"
                >
                  <MessageSquare className="h-4 w-4" />
                  <span>Ask AI About This Document</span>
                </Link>
              </div>

              {/* Status & Processing Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Processing Status</span>
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle className="h-4 w-4" />
                    <span>{document.status}</span>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Indexed Vector Chunks</span>
                  <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
                    <Layers className="h-4 w-4" />
                    <span>{document.chunks?.length || 0} chunks ready</span>
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase">Document Scope</span>
                  <div className="flex items-center gap-2 text-purple-400 font-bold text-sm">
                    <BookOpen className="h-4 w-4" />
                    <span>Clinical / Educational</span>
                  </div>
                </div>
              </div>

              {/* Extracted Document Summary */}
              {document.summary && (
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
                    <Sparkles className="h-4 w-4" />
                    <span>Document Executive Summary</span>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                    {document.summary}
                  </p>
                </div>
              )}

              {/* Chunk Inspector */}
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-cyan-400" />
                    <h2 className="text-base font-bold text-white">
                      Extracted Text Chunks ({document.chunks?.length || 0})
                    </h2>
                  </div>
                  <span className="text-xs text-slate-400">Source ground for hybrid vector search</span>
                </div>

                {(!document.chunks || document.chunks.length === 0) ? (
                  <div className="py-8 text-center text-xs text-slate-500">
                    No chunk details stored in preview.
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {document.chunks.map((c, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/70 text-xs text-slate-300 space-y-1.5"
                      >
                        <div className="flex items-center justify-between text-[11px] text-cyan-400 font-semibold">
                          <span>Chunk #{c.chunk_index ?? idx + 1} — Section: {c.section_heading || "General"}</span>
                          <span className="text-slate-400">Page {c.page_number || 1}</span>
                        </div>
                        <p className="leading-relaxed text-slate-300 font-mono text-[11px] whitespace-pre-wrap">
                          {c.content}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
