"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Navbar } from "../../components/Navbar";
import { Sidebar } from "../../components/Sidebar";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { CitationCard } from "../../components/CitationCard";
import {
  getConversations,
  getConversationMessages,
  getDocuments,
  deleteConversation,
  ConversationItem,
  DocumentItem,
  ChatMessage,
} from "../../lib/api";
import { getAuthToken, ensureAuthenticatedSession, clearAuthSession } from "../../lib/auth";
import {
  Send,
  Sparkles,
  Bot,
  User,
  Trash2,
  FileText,
  AlertCircle,
  RefreshCw,
  PlusCircle,
  Clock,
  Layers,
} from "lucide-react";

function ChatContent() {
  const searchParams = useSearchParams();
  const initialDocId = searchParams.get("docId") || "";
  const initialConvoId = searchParams.get("id") || "";

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConvoId, setActiveConvoId] = useState<string>(initialConvoId);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>(initialDocId);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [activeAgent, setActiveAgent] = useState("Medical Orchestrator");
  const [currentCitations, setCurrentCitations] = useState<any[]>([]);
  const [errorMsg, setErrorMsg] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ensureAuthenticatedSession().then(() => {
      loadSidebarData();
    });
  }, []);

  useEffect(() => {
    if (activeConvoId) {
      loadConversation(activeConvoId);
    } else {
      setMessages([]);
      setCurrentCitations([]);
    }
  }, [activeConvoId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  async function loadSidebarData() {
    try {
      const [convos, docsRes] = await Promise.all([
        getConversations().catch(() => []),
        getDocuments().catch(() => ({ total: 0, documents: [] })),
      ]);
      setConversations(Array.isArray(convos) ? convos : []);
      const docList = Array.isArray(docsRes) ? docsRes : (docsRes?.documents || []);
      setDocuments(docList);
      if (initialConvoId && Array.isArray(convos) && convos.some((c) => c.id === initialConvoId)) {
        setActiveConvoId(initialConvoId);
      }
    } catch (err) {
      console.error("Error loading sidebar data:", err);
    }
  }

  async function loadConversation(convoId: string) {
    try {
      setLoading(true);
      const res = await getConversationMessages(convoId);
      setMessages(res.messages || []);
      // Collect citations from assistant messages
      const lastAssistant = res.messages.filter((m) => m.role === "assistant").pop();
      if (lastAssistant && lastAssistant.citations) {
        setCurrentCitations(lastAssistant.citations);
      } else {
        setCurrentCitations([]);
      }
    } catch (err) {
      console.error("Error loading conversation:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSendMessage(e?: React.FormEvent) {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userText = inputMessage.trim();
    setInputMessage("");
    setErrorMsg("");

    // Add user message to UI
    const newUserMsg: ChatMessage = {
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMsg]);
    setLoading(true);
    setStreamingText("");
    setCurrentCitations([]);

    let token = getAuthToken();
    if (!token) {
      token = await ensureAuthenticatedSession();
    }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    try {
      // Use SSE streaming endpoint
      let response = await fetch(`${apiUrl}/api/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: userText,
          conversation_id: activeConvoId || null,
          document_id: selectedDocId || null,
        }),
      });

      // Transparent recovery if session is unauthenticated or expired
      if (response.status === 401) {
        clearAuthSession();
        const freshToken = await ensureAuthenticatedSession();
        if (freshToken) {
          token = freshToken;
          response = await fetch(`${apiUrl}/api/chat/stream`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${freshToken}`,
            },
            body: JSON.stringify({
              message: userText,
              conversation_id: activeConvoId || null,
              document_id: selectedDocId || null,
            }),
          });
        }
      }

      if (!response.ok) {
        throw new Error(`Chat request failed (HTTP ${response.status})`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder("utf-8");
      let fullAssistantText = "";
      let parsedCitations: any[] = [];
      let convoId = activeConvoId;

      if (reader) {
        let done = false;
        let buffer = "";

        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          if (value) {
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.replace("data: ", ""));
                  if (data.type === "meta" || data.type === "metadata") {
                    convoId = data.conversation_id;
                    if (!activeConvoId && data.conversation_id) {
                      setActiveConvoId(data.conversation_id);
                    }
                    if (data.agent) {
                      setActiveAgent(data.agent);
                    }
                    if (data.citations) {
                      parsedCitations = data.citations || [];
                      setCurrentCitations(parsedCitations);
                    }
                  } else if (data.type === "token") {
                    const tokenText = data.content !== undefined ? data.content : (data.token || "");
                    fullAssistantText += tokenText;
                    setStreamingText(fullAssistantText);
                  } else if (data.type === "agent") {
                    setActiveAgent(data.agent);
                  } else if (data.type === "citations") {
                    parsedCitations = data.citations || [];
                    setCurrentCitations(parsedCitations);
                  }
                } catch {
                  // ignore JSON parse chunk fragment
                }
              }
            }
          }
        }
      }

      // Add complete assistant message to list
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: fullAssistantText || "Response complete.",
        citations: parsedCitations,
        agent: activeAgent,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setStreamingText("");
      loadSidebarData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process chat request.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteConvo(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm("Delete this conversation?")) return;
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConvoId === id) {
        setActiveConvoId("");
        setMessages([]);
        setCurrentCitations([]);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />

        {/* Chat conversations sub-sidebar */}
        <div className="w-64 border-r border-slate-800 bg-slate-900/40 p-3 hidden lg:flex flex-col justify-between">
          <div className="space-y-3">
            <button
              onClick={() => {
                setActiveConvoId("");
                setMessages([]);
                setCurrentCitations([]);
              }}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md shadow-cyan-600/20 transition"
            >
              <PlusCircle className="h-4 w-4" />
              <span>New Conversation</span>
            </button>

            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500 px-2 tracking-wider">
                Saved Sessions
              </span>
              <div className="max-h-[calc(100vh-280px)] overflow-y-auto space-y-1 pr-1">
                {(conversations || []).length === 0 ? (
                  <div className="text-xs text-slate-500 px-2 py-3">No conversations yet</div>
                ) : (
                  (conversations || []).map((c) => (
                    <div
                      key={c.id}
                      onClick={() => setActiveConvoId(c.id)}
                      className={`group flex items-center justify-between p-2 rounded-lg text-xs cursor-pointer transition ${
                        activeConvoId === c.id
                          ? "bg-cyan-500/15 text-cyan-300 font-medium border border-cyan-500/30"
                          : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                      }`}
                    >
                      <span className="truncate max-w-[150px]">{c.title || "Medical Query"}</span>
                      <button
                        onClick={(e) => handleDeleteConvo(c.id, e)}
                        className="opacity-0 group-hover:opacity-100 hover:text-red-400 transition"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Main Chat Interface */}
        <div className="flex-1 flex flex-col h-[calc(100vh-100px)]">
          {/* Top Filter Bar */}
          <div className="h-14 border-b border-slate-800 px-6 flex items-center justify-between bg-slate-900/60">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-400">Target Document Context:</span>
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="">All Uploaded Documents (Global Hybrid Search)</option>
                {(documents || []).map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.filename || "Document"} ({d.file_type ? d.file_type.toUpperCase() : "TXT"})
                  </option>
                ))}
              </select>
            </div>

            <div className="hidden sm:flex items-center gap-2 text-xs text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2.5 py-1 rounded-full">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Active Agent: {activeAgent}</span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && !streamingText && (
              <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-4 text-slate-400">
                <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-400">
                  <Bot className="h-10 w-10" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">MedAssist AI Intelligence</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Ask questions grounded in your uploaded clinical documents. Answers provide verifiable citations and strict non-diagnostic health education.
                  </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left w-full mt-4">
                  {[
                    "What are the clinical symptoms described in Section 2?",
                    "Summarize the patient cohort outcomes in the document.",
                    "Explain what dyspnea means in everyday language.",
                    "Compare LDL and HDL cholesterol functions.",
                  ].map((sample, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputMessage(sample)}
                      className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-xs text-slate-300 text-left transition"
                    >
                      &ldquo;{sample}&rdquo;
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-3 max-w-4xl mx-auto ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="h-8 w-8 rounded-lg bg-cyan-600 flex items-center justify-center text-white shrink-0 mt-1">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed max-w-[85%] ${
                    msg.role === "user"
                      ? "bg-cyan-600 text-white rounded-br-none shadow-md shadow-cyan-600/20"
                      : "bg-slate-900 border border-slate-800 rounded-bl-none text-slate-200"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>

                  {/* Assistant Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
                      <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1.5">
                        <Layers className="h-3.5 w-3.5" />
                        <span>Source Grounding & Citations:</span>
                      </div>
                      <div className="grid grid-cols-1 gap-2">
                        {msg.citations.map((c, cIdx) => (
                          <CitationCard key={cIdx} citation={c} index={cIdx + 1} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}

            {/* Live Streaming Assistant Output */}
            {streamingText && (
              <div className="flex gap-3 max-w-4xl mx-auto justify-start">
                <div className="h-8 w-8 rounded-lg bg-cyan-600 flex items-center justify-center text-white shrink-0 mt-1">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="p-4 rounded-2xl text-sm leading-relaxed max-w-[85%] bg-slate-900 border border-slate-800 rounded-bl-none text-slate-200">
                  <div className="whitespace-pre-wrap">{streamingText}</div>
                  <div className="flex items-center gap-1 mt-2 text-xs text-cyan-400 animate-pulse">
                    <RefreshCw className="h-3 w-3 animate-spin" />
                    <span>Synthesizing response...</span>
                  </div>
                </div>
              </div>
            )}

            {errorMsg && (
              <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-400 flex flex-col sm:flex-row sm:items-center justify-between gap-3 max-w-4xl mx-auto shadow-sm">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
                {(errorMsg.includes("401") || errorMsg.includes("Unauthorized") || errorMsg.includes("failed")) && (
                  <button
                    type="button"
                    onClick={async () => {
                      setErrorMsg("");
                      const token = await ensureAuthenticatedSession();
                      if (token) {
                        loadSidebarData();
                      }
                    }}
                    className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold transition shrink-0 self-start sm:self-auto shadow-sm"
                  >
                    Authenticate Demo Session
                  </button>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div className="p-4 border-t border-slate-800 bg-slate-900/40">
            <form onSubmit={handleSendMessage} className="max-w-4xl mx-auto flex items-center gap-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about document findings, medical concepts, or summaries..."
                className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition shadow-inner"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !inputMessage.trim()}
                className="px-5 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-medium text-sm transition flex items-center gap-2 shadow-lg shadow-cyan-600/20"
              >
                {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                <span>Send</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs">
          <RefreshCw className="h-5 w-5 animate-spin text-cyan-400 mr-2" />
          <span>Loading MedAssist AI Chat...</span>
        </div>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
