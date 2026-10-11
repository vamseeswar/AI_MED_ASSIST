"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import {
  performSearch,
  getDocuments,
  SearchResult,
  DocumentItem,
} from "../../lib/api";
import {
  Search as SearchIcon,
  Filter,
  FileText,
  MessageSquare,
  Sparkles,
  Layers,
  ArrowRight,
  RefreshCw,
} from "lucide-react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [searchMode, setSearchMode] = useState<"hybrid" | "semantic" | "keyword">("hybrid");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    getDocuments()
      .then((res) => setDocuments(res.documents || []))
      .catch(() => {});
  }, []);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setSearched(true);
    try {
      const data = await performSearch(query.trim(), searchMode, selectedDocId || undefined);
      setResults(data.results || []);
    } catch (err) {
      console.error("Search failed:", err);
      setResults([]);
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
              Hybrid Medical Search Engine
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Cross-document retrieval using Reciprocal Rank Fusion (RRF) between Dense Embeddings and BM25 Sparse Keyword search.
            </p>
          </div>

          {/* Search Box & Controls */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-sm">
            <form onSubmit={handleSearch} className="flex gap-3">
              <div className="relative flex-1">
                <SearchIcon className="h-5 w-5 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search symptoms, clinical observations, biomarkers, or guidelines..."
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-12 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition shadow-inner"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-semibold text-sm transition flex items-center gap-2 shadow-lg shadow-cyan-600/20"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <SearchIcon className="h-4 w-4" />}
                <span>Search</span>
              </button>
            </form>

            {/* Filter controls */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800/60 text-xs">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                  <Filter className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Retrieval Mode:</span>
                </span>
                <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800">
                  {(["hybrid", "semantic", "keyword"] as const).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => setSearchMode(mode)}
                      className={`px-3 py-1 rounded-md text-xs font-semibold capitalize transition ${
                        searchMode === mode
                          ? "bg-cyan-600 text-white shadow-sm"
                          : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-400">Document Scope:</span>
                <select
                  value={selectedDocId}
                  onChange={(e) => setSelectedDocId(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="">All Uploaded Documents</option>
                  {documents.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.filename}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Results List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                <span>Search Results {searched && `(${results.length})`}</span>
              </h2>
              {searched && (
                <span className="text-xs text-slate-400">
                  Mode: <strong className="text-cyan-400 uppercase">{searchMode}</strong>
                </span>
              )}
            </div>

            {loading ? (
              <div className="py-16 text-center text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="h-5 w-5 animate-spin text-cyan-400" />
                <span>Executing hybrid retrieval across vector and keyword indices...</span>
              </div>
            ) : searched && results.length === 0 ? (
              <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-500 text-sm">
                No matching passages found. Try a different query or select All Documents.
              </div>
            ) : !searched ? (
              <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-500 text-sm">
                Enter a clinical query above to retrieve source-grounded passages.
              </div>
            ) : (
              <div className="space-y-3">
                {results.map((res, idx) => (
                  <div
                    key={idx}
                    className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-cyan-500/40 transition space-y-3 shadow-sm"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-cyan-400" />
                        <span className="font-bold text-white">
                          {res.document_name || "Medical Document"}
                        </span>
                        <span className="text-slate-400">
                          • Page {res.page_number} • Section: {res.section_heading}
                        </span>
                      </div>
                      {res.relevance_score != null && (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          {(res.relevance_score * 100).toFixed(0)}% Relevance
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/60">
                      {res.content}
                    </p>

                    <div className="flex items-center justify-between pt-1">
                      <span className="text-[11px] text-slate-400">Chunk #{res.chunk_index}</span>
                      <Link
                        href={`/chat?docId=${res.document_id}`}
                        className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
                      >
                        <span>Ask AI about this passage</span>
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
