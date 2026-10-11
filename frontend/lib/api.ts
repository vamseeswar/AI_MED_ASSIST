import { authHeader, ensureAuthenticatedSession } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  let headers = {
    ...authHeader(),
    ...(options.headers || {}),
  };

  let res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // If 401 and not a login request, try auto demo recovery
  if (res.status === 401 && !endpoint.includes("/auth/login")) {
    const token = await ensureAuthenticatedSession();
    if (token) {
      headers = {
        ...headers,
        Authorization: `Bearer ${token}`,
      };
      res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });
    }
  }

  if (!res.ok) {
    let errMessage = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errData = await res.json();
      if (errData.detail) {
        errMessage = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errMessage);
  }

  return res.json();
}

// Documents
export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  page_count: number;
  word_count: number;
  title?: string;
  summary?: string;
  created_at: string;
}

export async function getDocuments(): Promise<{ total: number; documents: DocumentItem[] }> {
  const data = await apiRequest<any>("/api/documents");
  if (Array.isArray(data)) {
    return { total: data.length, documents: data };
  }
  return {
    total: data?.total || (data?.documents ? data.documents.length : 0),
    documents: data?.documents || [],
  };
}

export async function getDocumentById(id: string): Promise<DocumentItem & { chunks?: any[] }> {
  return apiRequest<DocumentItem & { chunks?: any[] }>(`/api/documents/${id}`);
}

export async function deleteDocument(id: string): Promise<{ success: boolean }> {
  return apiRequest<{ success: boolean }>(`/api/documents/${id}`, { method: "DELETE" });
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);

  const token = typeof window !== "undefined" ? localStorage.getItem("medassist_token") : null;
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    let msg = "Upload failed";
    try {
      const data = await res.json();
      if (data.detail) msg = data.detail;
    } catch {}
    throw new Error(msg);
  }

  return res.json();
}

// Search
export interface SearchResult {
  document_id: string;
  document_name: string;
  chunk_index: number;
  content: string;
  page_number: number;
  section_heading: string;
  relevance_score?: number;
  search_mode?: string;
}

export async function performSearch(
  query: string,
  mode: "hybrid" | "semantic" | "keyword" = "hybrid",
  documentId?: string
): Promise<{ query: string; total_results: number; search_mode: string; results: SearchResult[] }> {
  return apiRequest("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, mode, document_id: documentId || null }),
  });
}

// Chat
export interface ChatMessage {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: any[];
  agent?: string;
  processing_time_ms?: number;
  created_at?: string;
}

export interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export async function getConversations(): Promise<ConversationItem[]> {
  return apiRequest<ConversationItem[]>("/api/chat/conversations");
}

export async function getConversationMessages(convoId: string): Promise<{ conversation_id: string; messages: ChatMessage[] }> {
  return apiRequest(`/api/chat/conversations/${convoId}`);
}

export async function deleteConversation(convoId: string): Promise<{ success: boolean }> {
  return apiRequest(`/api/chat/conversations/${convoId}`, { method: "DELETE" });
}

export async function sendChatMessage(
  message: string,
  conversationId?: string,
  documentId?: string
): Promise<{
  conversation_id: string;
  answer: string;
  agent: string;
  citations: any[];
  processing_time_ms: number;
}> {
  return apiRequest("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
      document_id: documentId || null,
    }),
  });
}

// Observability & Admin
export interface SystemMetrics {
  status: string;
  counts: {
    users: number;
    documents: number;
    chunks: number;
    conversations: number;
    messages: number;
    audit_logs: number;
  };
  job_status_breakdown: Record<string, number>;
  audit_action_breakdown: Record<string, number>;
  document_type_breakdown: Record<string, number>;
}

export async function getSystemMetrics(): Promise<SystemMetrics> {
  return apiRequest<SystemMetrics>("/api/admin/metrics");
}

export async function getAuditLogs(limit = 50, offset = 0): Promise<{ total: number; items: any[] }> {
  return apiRequest(`/api/admin/audit-logs?limit=${limit}&offset=${offset}`);
}

export async function getEvaluationResults(): Promise<any> {
  return apiRequest("/api/admin/evaluation");
}

export async function runEvaluationBenchmark(): Promise<any> {
  return apiRequest("/api/admin/evaluation/run", { method: "POST" });
}

// ML / DL Classify
export async function classifyDocumentML(text: string): Promise<any> {
  return apiRequest("/api/ml/classify-document", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function classifyDocumentDL(text: string): Promise<any> {
  return apiRequest("/api/dl/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}
