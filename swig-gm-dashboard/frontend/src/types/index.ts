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

// Hourly detail types
export interface HourlyDetail {
  hour: number;
  hour_label: string;
  date: string;
  transactions: {
    count: number;
    revenue: number;
    avg_ticket: number;
  };
  staff: Array<{
    employee_id: number;
    name: string;
    role: string;
  }>;
  top_items: Array<{
    name: string;
    quantity: number;
    revenue: number;
  }>;
  channels: Array<{
    channel: string;
    count: number;
    percentage: number;
    revenue: number;
  }>;
  drive_thru: {
    avg_service_seconds: number | null;
    cars_served: number;
  };
  labor: {
    staff_count: number;
    hourly_cost: number;
  };
}

// Roster types
export interface RosterEntry {
  employee_id: number;
  name: string;
  role: string;
  job_role: string;
  is_minor: boolean;
  hourly_wage: number;
  schedule: {
    start: string | null;
    end: string | null;
    hours: number;
  };
  actual: {
    clock_in: string | null;
    clock_out: string | null;
    hours: number;
  };
  variance: number;
  break: {
    taken: boolean;
    start: string | null;
    end: string | null;
    duration_minutes: number | null;
    compliant: boolean;
  };
  attendance: {
    is_late: boolean;
    late_minutes: number;
    is_no_show: boolean;
  };
  labor_cost: number;
  violations: Array<{
    type: string;
    description: string;
    penalty: number;
  }>;
}

export interface RosterData {
  date: string;
  roster: RosterEntry[];
  summary: {
    employee_count: number;
    total_scheduled_hours: number;
    total_actual_hours: number;
    hours_variance: number;
    total_labor_cost: number;
    late_arrivals: number;
    no_shows: number;
    break_violations: number;
  };
  role_distribution: Array<{
    role: string;
    count: number;
  }>;
}

// Sales types
export interface SalesByCategory {
  date: string;
  total_revenue: number;
  by_category: Array<{
    category: string;
    transaction_count: number;
    quantity_sold: number;
    revenue: number;
    percentage: number;
  }>;
  by_item_type: Array<{
    type: string;
    quantity: number;
    revenue: number;
  }>;
}

export interface PaymentBreakdown {
  date: string;
  summary: {
    total_transactions: number;
    total_amount: number;
    total_tips: number;
    tip_percentage: number;
  };
  by_method: Array<{
    method: string;
    transaction_count: number;
    percentage: number;
    total_amount: number;
    tips: number;
    avg_amount: number;
  }>;
}

export interface LoyaltyStats {
  date: string;
  total_transactions: number;
  loyalty: {
    transactions: number;
    percentage: number;
    revenue: number;
    avg_ticket: number;
  };
  non_loyalty: {
    transactions: number;
    percentage: number;
    revenue: number;
    avg_ticket: number;
  };
}

export interface TopItem {
  rank: number;
  item_name: string;
  item_type: string;
  quantity_sold: number;
  revenue: number;
}

// Inventory types
export interface IngredientUsage {
  inventory_id: number;
  ingredient_name: string;
  category: string;
  quantity_used: number;
  unit: string;
  cost: number;
}

export interface COGSSummary {
  date: string;
  total_revenue: number;
  total_cogs: number;
  cogs_percentage: number;
  gross_profit: number;
  gross_margin: number;
  by_category: Array<{
    category: string;
    cost: number;
    percentage: number;
  }>;
}

export interface UsageByCategory {
  category: string;
  item_count: number;
  total_cost: number;
  top_items: Array<{
    name: string;
    quantity: number;
    unit: string;
    cost: number;
  }>;
}

// Weekly types
export interface WeeklySummary {
  week_start: string;
  week_end: string;
  store_id: number;
  sales: {
    total_revenue: number;
    transaction_count: number;
    avg_ticket: number;
    days_with_sales: number;
    loyalty_transactions: number;
    loyalty_percentage: number;
  };
  labor: {
    total_hours: number;
    total_cost: number;
    labor_percentage: number;
    employees_worked: number;
  };
  compliance: {
    violation_count: number;
    total_penalties: number;
  };
  top_items: Array<{
    name: string;
    quantity: number;
    revenue: number;
  }>;
}

export interface WeeklyTrend {
  date: string;
  day_name: string;
  transactions: number;
  revenue: number;
  avg_ticket: number;
  labor_hours: number;
  labor_cost: number;
  labor_percentage: number;
}

export interface WeeklyTrends {
  week_start: string;
  week_end: string;
  daily: WeeklyTrend[];
}

export interface WeeklyComparison {
  current_week: {
    start: string;
    end: string;
    transactions: number;
    revenue: number;
    avg_ticket: number;
    labor_cost: number;
  };
  previous_week: {
    start: string;
    end: string;
    transactions: number;
    revenue: number;
    avg_ticket: number;
    labor_cost: number;
  };
  changes: {
    transactions: number;
    revenue: number;
    avg_ticket: number;
    labor_cost: number;
  };
}
