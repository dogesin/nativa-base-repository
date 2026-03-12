/**
 * Cliente HTTP base. Usado por features/X/services para llamadas a la API.
 * Configuración centralizada (baseURL, headers, interceptors).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export const apiClient = {
  baseURL: API_BASE,

  async get<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseURL}${path}`, {
      ...options,
      method: "GET",
      headers: { "Content-Type": "application/json", ...options?.headers },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async post<T>(path: string, data?: unknown, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseURL}${path}`, {
      ...options,
      method: "POST",
      headers: { "Content-Type": "application/json", ...options?.headers },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async patch<T>(path: string, data?: unknown, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseURL}${path}`, {
      ...options,
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...options?.headers },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async delete(path: string, options?: RequestInit): Promise<void> {
    const res = await fetch(`${this.baseURL}${path}`, { ...options, method: "DELETE" });
    if (!res.ok) throw new Error(await res.text());
  },
};
