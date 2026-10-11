"use client";

import React from "react";
import { AlertTriangle, ShieldCheck } from "lucide-react";

export function DisclaimerBanner() {
  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-xs text-amber-300 flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
        <span>
          <strong className="font-semibold text-amber-200">Non-Diagnostic Educational System:</strong>{" "}
          MedAssist AI provides source-grounded document intelligence and health education. It does NOT diagnose medical conditions, prescribe medications, or replace professional clinical judgment.
        </span>
      </div>
      <div className="hidden md:flex items-center gap-1.5 text-xs text-emerald-400 font-medium shrink-0">
        <ShieldCheck className="h-3.5 w-3.5" />
        <span>Strict Clinical Boundaries Active</span>
      </div>
    </div>
  );
}
