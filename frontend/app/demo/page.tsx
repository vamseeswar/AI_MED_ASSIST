"use client";

import React from "react";
import Link from "next/link";
import { Download, Film, ArrowLeft, CheckCircle2, ShieldAlert } from "lucide-react";

export default function DemoDownloadPage() {
  const formats = [
    {
      title: "MP4 High Definition Video",
      desc: "Standard 1080p MP4 format. Perfect for LinkedIn, YouTube, and presentations.",
      size: "5.1 MB",
      filename: "medassist_demo.mp4",
      url: "/medassist_demo.mp4",
      recommended: true,
      badge: "Best for LinkedIn"
    },
    {
      title: "Animated GIF",
      desc: "Lightweight looping animated GIF. Autoplays in web articles and posts.",
      size: "4.0 MB",
      filename: "medassist_demo.gif",
      url: "/medassist_demo.gif",
      recommended: false,
      badge: "Autoplay Ready"
    },
    {
      title: "Original WebP Recording",
      desc: "Original high-fidelity browser recording with full color fidelity.",
      size: "4.1 MB",
      filename: "medassist_demo.webp",
      url: "/medassist_demo.webp",
      recommended: false,
      badge: "Lossless Master"
    }
  ];

  return (
    <div className="min-w-full min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-3xl space-y-8">
        
        <div className="flex items-center justify-between">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 text-sm font-semibold transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <span className="text-xs text-slate-500 font-mono">MedAssist AI v1.0.0</span>
        </div>

        <div className="text-center space-y-3">
          <div className="inline-flex p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-2">
            <Film className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Download Platform Demo Video
          </h1>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            Choose your preferred format below to download the interactive 30-second walkthrough demo of MedAssist AI.
          </p>
        </div>

        {/* Video Preview Card */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl overflow-hidden space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Live Walkthrough Preview
            </span>
            <span className="font-mono">Duration: 30s • 1920x924</span>
          </div>
          <div className="rounded-xl overflow-hidden border border-slate-800/80 bg-black flex items-center justify-center">
            <video
              src="/medassist_demo.mp4"
              controls
              autoPlay
              loop
              muted
              className="w-full max-h-[360px] object-contain"
            />
          </div>
        </div>

        {/* Download Options Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {formats.map((f) => (
            <div
              key={f.filename}
              className={`p-5 rounded-2xl border flex flex-col justify-between transition-all ${
                f.recommended
                  ? "bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-950/20 ring-1 ring-cyan-500/30"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span
                    className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      f.recommended
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {f.badge}
                  </span>
                  <span className="text-xs font-mono text-slate-400">{f.size}</span>
                </div>
                <h3 className="font-bold text-slate-100 text-sm">{f.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
              </div>

              <div className="pt-4">
                <a
                  href={f.url}
                  download={f.filename}
                  className={`w-full py-2.5 px-3 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition ${
                    f.recommended
                      ? "bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md font-bold"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                  }`}
                >
                  <Download className="w-3.5 h-3.5" />
                  Download {f.filename.split(".").pop()?.toUpperCase()}
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Desktop notification */}
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 text-xs text-slate-400 flex items-start gap-3">
          <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div>
            <span className="text-slate-200 font-medium">Already saved to your PC: </span>
            The video has also been automatically saved directly to your Windows Desktop at:
            <code className="block mt-1 p-2 rounded bg-slate-950 text-cyan-300 font-mono text-[11px] break-all border border-slate-800">
              C:\Users\vamseeswara reddy\OneDrive\Desktop\medassist_demo.mp4
            </code>
          </div>
        </div>

      </div>
    </div>
  );
}
