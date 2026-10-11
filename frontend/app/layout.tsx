import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedAssist AI — Medical Document Intelligence Platform",
  description:
    "AI-Powered Medical Information & Document Intelligence Platform for healthcare research, document extraction, hybrid RAG, and clinical terminology insight.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-slate-950 text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
