"use client";

import React from "react";
import { FileText, Bookmark, CheckCircle2 } from "lucide-react";

interface CitationCardProps {
  citation: {
    document_id?: string;
    document_name?: string;
    page_number?: number;
    section_heading?: string;
    snippet?: string;
    relevance_score?: number;
  };
  index?: number;
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const docName = citation.document_name || "Medical Document";
  const page = citation.page_number ? `Page ${citation.page_number}` : "General Section";
  const section = citation.section_heading ? ` • ${citation.section_heading}` : "";
  const score = citation.relevance_score != null ? `${(citation.relevance_score * 100).toFixed(0)}% Match` : null;

  return (
    <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-700/60 hover:border-cyan-500/40 transition shadow-sm space-y-2">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-cyan-300">
          <FileText className="h-3.5 w-3.5 text-cyan-400" />
          <span className="truncate max-w-[200px]">{docName}</span>
          <span className="text-slate-400 font-normal">[{page}{section}]</span>
        </div>
        {score && (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {score}
          </span>
        )}
      </div>

      {citation.snippet && (
        <p className="text-xs text-slate-300 italic bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 line-clamp-3">
          &ldquo;{citation.snippet}&rdquo;
        </p>
      )}

      <div className="flex items-center gap-1 text-[10px] text-slate-400 font-medium">
        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
        <span>Grounded in uploaded document context</span>
      </div>
    </div>
  );
}
