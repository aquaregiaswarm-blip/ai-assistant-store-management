import type { Store, KPIs, HourlyData, Alert, Employee, Violation, SuggestedQuery } from '../types';

const API_BASE = '/api';

// Generic fetch helper
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

// Dashboard endpoints
export async function getStores(): Promise<Store[]> {
  return fetchAPI<Store[]>('/dashboard/stores');
}

export async function getKPIs(storeId: number, date?: string): Promise<KPIs> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<KPIs>(`/dashboard/kpis?${params}`);
}

export async function getHourlyData(storeId: number, date?: string): Promise<HourlyData[]> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<HourlyData[]>(`/dashboard/hourly?${params}`);
}

export async function getAlerts(storeId: number, date?: string): Promise<Alert[]> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<Alert[]>(`/dashboard/alerts?${params}`);
}

// Workforce endpoints
export async function getWhosWorking(storeId: number, date?: string): Promise<Employee[]> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<Employee[]>(`/workforce/whos-working?${params}`);
}

export async function getViolations(storeId: number, daysBack: number = 7): Promise<Violation[]> {
  const params = new URLSearchParams({
    store_id: storeId.toString(),
    days_back: daysBack.toString(),
  });
  return fetchAPI<Violation[]>(`/workforce/compliance/violations?${params}`);
}

// Chat endpoints
export async function sendChatMessage(
  message: string,
  storeId: number,
  sessionId?: string
): Promise<{ response: string; session_id: string }> {
  return fetchAPI('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      store_id: storeId,
      session_id: sessionId,
    }),
  });
}

export async function getSuggestedQueries(): Promise<SuggestedQuery[]> {
  return fetchAPI<SuggestedQuery[]>('/chat/suggested-queries');
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetchAPI(`/chat/session/${sessionId}`, { method: 'DELETE' });
}
