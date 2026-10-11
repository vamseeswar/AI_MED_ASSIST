"use client";

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  role: "USER" | "ADMIN" | "DOCTOR";
  is_active: boolean;
  created_at: string;
}

const TOKEN_KEY = "medassist_token";
const USER_KEY = "medassist_user";

export function setAuthSession(token: string, user: UserProfile) {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    window.dispatchEvent(new Event("auth-changed"));
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

export function getCurrentUser(): UserProfile | null {
  if (typeof window !== "undefined") {
    const raw = localStorage.getItem(USER_KEY);
    if (raw) {
      try {
        return JSON.parse(raw);
      } catch {
        return null;
      }
    }
  }
  return null;
}

export function clearAuthSession() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.dispatchEvent(new Event("auth-changed"));
  }
}

export function authHeader(): HeadersInit {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Ensures an active session exists. If not, transparently authenticates with
 * the pre-seeded demo doctor account to prevent 401 unauthorized errors.
 */
export async function ensureAuthenticatedSession(): Promise<string> {
  const existingToken = getAuthToken();
  if (existingToken) return existingToken;

  if (typeof window === "undefined") return "";

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "demo@medassist.ai",
        password: "DemoPassword123!",
      }),
    });

    if (res.ok) {
      const data = await res.json();
      const userProfile: UserProfile = {
        id: "demo-doctor-id",
        email: "demo@medassist.ai",
        full_name: "Dr. Sarah Chen, MD",
        role: (data.role as any) || "DOCTOR",
        is_active: true,
        created_at: new Date().toISOString(),
      };
      setAuthSession(data.access_token, userProfile);
      return data.access_token;
    }
  } catch (err) {
    console.warn("Auto demo session initialization failed:", err);
  }
  return "";
}
