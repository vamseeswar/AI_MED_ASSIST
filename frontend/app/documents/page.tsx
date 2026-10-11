"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import {
  getDocuments,
  uploadDocument,
  deleteDocument,
  DocumentItem,
} from "../../lib/api";
import {
  FileText,
  UploadCloud,
  Trash2,
  ExternalLink,
  MessageSquare,
  CheckCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Search,
} from "lucide-react";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  async function loadDocs() {
    try {
      setLoading(true);
      const res = await getDocuments();
      setDocuments(res.documents || []);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    await doUpload(file);
  }

  async function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    if (!e.dataTransfer.files || e.dataTransfer.files.length === 0) return;
    const file = e.dataTransfer.files[0];
    await doUpload(file);
  }

  async function doUpload(file: File) {
    setUploading(true);
    setUploadError("");
    try {
      await uploadDocument(file);
      await loadDocs();
    } catch (err: any) {
      setUploadError(err.message || "Document upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Delete document "${name}"?`)) return;
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  }

  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
              <h1 className="text-2xl md:text-3xl font-extrabold text-white">
                Medical Document Repository
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Upload clinical records, research papers, lab tests & reports for hybrid vector indexing and semantic Q&A.
              </p>
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 text-white text-sm font-semibold transition shadow-lg shadow-cyan-600/20"
            >
              {uploading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              <span>{uploading ? "Ingesting..." : "Upload New File"}</span>
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              className="hidden"
              accept=".pdf,.docx,.txt,.csv"
            />
          </div>

          {/* Upload Drag & Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="p-8 border-2 border-dashed border-slate-800 hover:border-cyan-500/60 rounded-2xl bg-slate-900/40 hover:bg-slate-900/70 transition flex flex-col items-center justify-center text-center cursor-pointer group"
          >
            <div className="p-3.5 rounded-2xl bg-cyan-500/10 text-cyan-400 group-hover:scale-110 transition">
              <UploadCloud className="h-8 w-8" />
            </div>
            <h3 className="text-base font-bold text-white mt-3">
              Drop medical files here or click to browse
            </h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md">
              Supported formats: PDF (with OCR fallback), DOCX, TXT, CSV. Max size: 25MB. Files are sanitized, chunked, and embedded securely.
            </p>
          </div>

          {uploadError && (
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          {/* Document Table & Search */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-cyan-400" />
                <h2 className="text-base font-bold text-white">Indexed Documents ({filteredDocs.length})</h2>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter by filename..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            {loading ? (
              <div className="py-12 text-center text-sm text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="h-4 w-4 animate-spin text-cyan-400" />
                <span>Loading documents...</span>
              </div>
            ) : filteredDocs.length === 0 ? (
              <div className="py-12 text-center text-sm text-slate-500">
                {searchTerm ? "No documents match the search term." : "No documents uploaded yet."}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider text-[10px] font-semibold">
                    <tr>
                      <th className="py-3 px-4 rounded-l-xl">File Name</th>
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Size</th>
                      <th className="py-3 px-4">Pages / Words</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Uploaded</th>
                      <th className="py-3 px-4 text-right rounded-r-xl">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredDocs.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3.5 px-4 font-semibold text-white">
                          <Link href={`/documents/${doc.id}`} className="hover:text-cyan-400 transition flex items-center gap-2">
                            <FileText className="h-4 w-4 text-cyan-400 shrink-0" />
                            <span className="truncate max-w-[200px]">{doc.filename}</span>
                          </Link>
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold uppercase text-[10px]">
                            {doc.file_type}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">
                          {(doc.file_size / 1024).toFixed(1)} KB
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">
                          {doc.page_count} pgs • {doc.word_count} words
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase flex items-center gap-1 w-fit ${
                              doc.status === "COMPLETED"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : doc.status === "PROCESSING"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                : doc.status === "FAILED"
                                ? "bg-red-500/10 text-red-400 border border-red-500/20"
                                : "bg-slate-800 text-slate-400"
                            }`}
                          >
                            {doc.status === "COMPLETED" && <CheckCircle className="h-3 w-3" />}
                            {doc.status === "PROCESSING" && <Clock className="h-3 w-3 animate-spin" />}
                            <span>{doc.status}</span>
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              href={`/chat?docId=${doc.id}`}
                              className="p-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 transition"
                              title="Ask AI about this document"
                            >
                              <MessageSquare className="h-3.5 w-3.5" />
                            </Link>
                            <Link
                              href={`/documents/${doc.id}`}
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                              title="View Document Details"
                            >
                              <ExternalLink className="h-3.5 w-3.5" />
                            </Link>
                            <button
                              onClick={() => handleDelete(doc.id, doc.filename)}
                              className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition"
                              title="Delete Document"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
