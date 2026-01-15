// Store types
export interface Store {
  store_id: number;
  store_name: string;
  city: string;
  state: string;
}

// KPI types
export interface KPIs {
  transactions: number;
  revenue: number;
  avg_ticket: number;
  throughput: number;
  labor_percentage: number;
  vs_yesterday: {
    transactions: number;
    revenue: number;
  };
  vs_last_week: {
    transactions: number;
    revenue: number;
  };
}

// Hourly data
export interface HourlyData {
  hour: number;
  hour_label: string;
  transactions: number;
  revenue: number;
  avg_ticket: number;
  is_peak: boolean;
}

// Alert types
export interface Alert {
  id: string;
  type: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  employee_name?: string;
}

// Workforce types
export interface Employee {
  employee_id: string;
  name: string;
  first_name: string;
  last_name: string;
  role: string;
  is_minor: boolean;
  clock_in?: string;
  clock_out?: string;
  hours_worked: number;
  still_working: boolean;
}

export interface Violation {
  violation_id: string;
  employee_id: string;
  employee_name: string;
  is_minor: boolean;
  date: string;
  type: string;
  description: string;
  penalty_cost: number;
  acknowledged: boolean;
  resolved: boolean;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface SuggestedQuery {
  text: string;
  category: string;
}
