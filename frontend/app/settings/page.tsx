"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { getCurrentUser, clearAuthSession, UserProfile } from "../../lib/auth";
import { useRouter } from "next/navigation";
import {
  Settings as SettingsIcon,
  User,
  Shield,
  Cpu,
  LogOut,
  Info,
  CheckCircle2,
} from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    setUser(getCurrentUser());
  }, []);

  function handleLogout() {
    clearAuthSession();
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-4xl mx-auto space-y-8 w-full">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Platform & User Settings
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Manage your profile, verify system runtime configurations, and inspect active safety filters.
            </p>
          </div>

          {/* User Profile Card */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <User className="h-5 w-5 text-cyan-400" />
              <span>User Profile & Credentials</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">Email Address</span>
                <div className="font-bold text-white text-sm">{user?.email || "Not signed in"}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">Access Role</span>
                <div className="font-bold text-cyan-400 text-sm uppercase">{user?.role || "USER"}</div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-semibold transition flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out of Current Session</span>
            </button>
          </div>

          {/* LLM Provider & API Key Configuration */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-white font-bold text-base">
                <Cpu className="h-5 w-5 text-amber-400" />
                <span>LLM Provider & API Key Configuration</span>
              </div>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Groq Active & Verified
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">Active Provider</span>
                <div className="font-bold text-amber-400 text-sm">Groq Cloud LPU</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">Active Model</span>
                <div className="font-bold text-white text-sm">openai/gpt-oss-120b</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">API Key Status</span>
                <div className="font-bold text-emerald-400 text-sm">Configured (Active)</div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/90 text-xs space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs">
                <Info className="h-4 w-4" />
                <span>Where to Add or Update API Keys:</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                API keys are securely configured in your workspace environment file:
                <code className="mx-1 px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[11px]">.env</code>
                located at <code className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-200 font-mono text-[11px]">c:\AI_MED_ASSIST\.env</code>.
              </p>
              <div className="p-3 rounded-lg bg-black/50 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1">
                <div><span className="text-purple-400">LLM_PROVIDER</span>=<span className="text-amber-300">&quot;groq&quot;</span></div>
                <div><span className="text-purple-400">GROQ_API_KEY</span>=<span className="text-emerald-300">&quot;your_groq_api_key_here&quot;</span></div>
                <div><span className="text-purple-400">LLM_MODEL</span>=<span className="text-amber-300">&quot;openai/gpt-oss-120b&quot;</span></div>
              </div>
              <p className="text-[11px] text-slate-400">
                You can also configure <code className="text-slate-300">GOOGLE_API_KEY</code> or <code className="text-slate-300">OPENAI_API_KEY</code>. The system includes automatic multi-model failover to ensure zero runtime interruptions.
              </p>
            </div>
          </div>

          {/* AI Runtime Architecture */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <Cpu className="h-5 w-5 text-purple-400" />
              <span>AI Engine & Retrieval Architecture</span>
            </div>

            <div className="space-y-2 text-xs">
              {[
                { label: "Active LLM Engine", val: "Groq Cloud (openai/gpt-oss-120b)" },
                { label: "LLM Orchestration Framework", val: "LangGraph Multi-Agent State Machine" },
                { label: "Retrieval Architecture", val: "Dense Vector (Cosine) + BM25 Sparse Keyword with RRF" },
                { label: "Reranker Model", val: "Cross-Encoder (ms-marco-MiniLM-L-6-v2 fallback)" },
                { label: "Tool Protocol", val: "Model Context Protocol (MCP) Standardized Servers" },
                { label: "Document Classification", val: "Scikit-Learn TF-IDF + PyTorch Transformer" },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800"
                >
                  <span className="text-slate-400">{item.label}</span>
                  <span className="font-bold text-slate-200">{item.val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Safety Policies */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <Shield className="h-5 w-5 text-emerald-400" />
              <span>Medical Safety Policies</span>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Diagnostic requests (&ldquo;Do I have X?&rdquo;) trigger explicit clinical refusal and referral to healthcare professionals.</span>
              </div>
              <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Prescription requests (&ldquo;What medication should I take?&rdquo;) are strictly rejected.</span>
              </div>
              <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Untrusted document encapsulations prevent system prompt overrides and prompt injection.</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
