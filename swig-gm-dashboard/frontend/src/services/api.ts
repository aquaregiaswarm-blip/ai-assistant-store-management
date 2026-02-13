import type {
  Store, KPIs, HourlyData, Alert, Employee, Violation, SuggestedQuery,
  HourlyDetail, RosterData, SalesByCategory, PaymentBreakdown, LoyaltyStats, TopItem,
  IngredientUsage, COGSSummary, UsageByCategory,
  WeeklySummary, WeeklyTrends, WeeklyComparison
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'https://swig-gm-dashboard-841327020312.us-east1.run.app/api';

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

export async function getViolations(storeId: number, daysBack: number = 7, date?: string): Promise<Violation[]> {
  const params = new URLSearchParams({
    store_id: storeId.toString(),
    days_back: daysBack.toString(),
  });
  if (date) params.append('date', date);
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

// Transaction detail endpoints
export async function getHourlyDetail(storeId: number, hour: number, date?: string): Promise<HourlyDetail> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<HourlyDetail>(`/transactions/hourly-detail/${hour}?${params}`);
}

export async function getSalesByCategory(storeId: number, date?: string): Promise<SalesByCategory> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<SalesByCategory>(`/transactions/sales-by-category?${params}`);
}

export async function getPaymentBreakdown(storeId: number, date?: string): Promise<PaymentBreakdown> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<PaymentBreakdown>(`/transactions/payment-breakdown?${params}`);
}

export async function getLoyaltyStats(storeId: number, date?: string): Promise<LoyaltyStats> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<LoyaltyStats>(`/transactions/loyalty-stats?${params}`);
}

export async function getTopItems(storeId: number, date?: string, limit: number = 10): Promise<TopItem[]> {
  const params = new URLSearchParams({
    store_id: storeId.toString(),
    limit: limit.toString()
  });
  if (date) params.append('date', date);
  return fetchAPI<TopItem[]>(`/transactions/top-items?${params}`);
}

// Workforce endpoints
export async function getRoster(storeId: number, date?: string): Promise<RosterData> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<RosterData>(`/workforce/roster?${params}`);
}

// Inventory endpoints
export async function getDailyUsage(storeId: number, date?: string): Promise<IngredientUsage[]> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<IngredientUsage[]>(`/inventory/daily-usage?${params}`);
}

export async function getCOGSSummary(storeId: number, date?: string): Promise<COGSSummary> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<COGSSummary>(`/inventory/cogs?${params}`);
}

export async function getUsageByCategory(storeId: number, date?: string): Promise<UsageByCategory[]> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<UsageByCategory[]>(`/inventory/usage-by-category?${params}`);
}

// Weekly endpoints
export async function getWeeklySummary(storeId: number, date?: string): Promise<WeeklySummary> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<WeeklySummary>(`/weekly/summary?${params}`);
}

export async function getWeeklyTrends(storeId: number, date?: string): Promise<WeeklyTrends> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<WeeklyTrends>(`/weekly/trends?${params}`);
}

export async function getWeeklyComparison(storeId: number, date?: string): Promise<WeeklyComparison> {
  const params = new URLSearchParams({ store_id: storeId.toString() });
  if (date) params.append('date', date);
  return fetchAPI<WeeklyComparison>(`/weekly/comparison?${params}`);
}
