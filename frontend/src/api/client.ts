const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
export type Product = { id?: string; name: string; price?: number; price_ngn?: number; stock?: number }
export type ActivityEvent = { id?: string; type: string; timestamp: string | Date; summary: string; data?: Record<string, unknown> }
export type KnowledgeGap = { id: string; question: string; type?: string; created_at?: string; timestamp?: string }
export type PendingOrder = { id?: string; order_ref: string; customer_name: string; items: string; total_ngn: number; created_at?: string; timestamp?: string }
export type BotSettings = { agent_name: string; agent_personality: string; agent_greeting: string; agent_language_style: string }
async function request<T>(path: string, init?: RequestInit): Promise<T> { const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) }, ...init }); if (!response.ok) throw new Error('Request failed'); return response.json() as Promise<T> }
export const api = {
  getSummary: () => request<Record<string, any>>('/api/dashboard/summary'), getOrders: () => request<Record<string, any>>('/api/dashboard/orders'), getConversations: () => request<Record<string, any>>('/api/dashboard/conversations'), getBrain: () => request<Record<string, any>>('/api/dashboard/brain'), getEscalations: () => request<Record<string, any>>('/api/dashboard/escalations'),
  getKnowledgeGaps: () => request<KnowledgeGap[] | { gaps: KnowledgeGap[] }>('/api/dashboard/knowledge-gaps'), resolveKnowledgeGap: (id: string, resolution: string) => request(`/api/dashboard/knowledge-gaps/${id}`, { method: 'PATCH', body: JSON.stringify({ resolved: true, resolution }) }),
  getPendingFulfillment: () => request<PendingOrder[] | { orders: PendingOrder[] }>('/api/dashboard/orders/pending-fulfillment'), getBotSettings: () => request<BotSettings>('/api/settings/bot'), updateBotSettings: (settings: BotSettings) => request('/api/settings/bot', { method: 'PATCH', body: JSON.stringify(settings) }),
  uploadDatabase: async (file: File) => { const body = new FormData(); body.append('file', file); const r = await fetch(`${API_BASE}/api/upload/database`, { method: 'POST', body }); if (!r.ok) throw new Error('Upload failed'); return r.json() }, confirmUpload: (data: unknown) => request('/api/upload/confirm', { method: 'POST', body: JSON.stringify(data) }),
  getExtendedBrain: () => request<Record<string, any>>('/api/settings/brain-extended'), updateExtendedBrain: (fields: Record<string, any>) => request('/api/settings/brain-extended', { method: 'PATCH', body: JSON.stringify(fields) }),
}
