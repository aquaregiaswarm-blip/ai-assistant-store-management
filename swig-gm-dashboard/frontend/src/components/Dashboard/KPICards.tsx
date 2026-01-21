import { DollarSign, ShoppingCart, Users, TrendingUp } from 'lucide-react';
import type { KPIs } from '../../types';

interface KPICardsProps {
  kpis: KPIs | undefined;
  isLoading: boolean;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function formatChange(value: number): { text: string; isPositive: boolean } {
  const sign = value >= 0 ? '+' : '';
  return { text: `${sign}${value.toFixed(1)}%`, isPositive: value >= 0 };
}

interface KPICardProps {
  title: string;
  value: string;
  change?: number;
  changeLabel?: string;
  icon: React.ReactNode;
  accentColor: 'red' | 'navy' | 'slate' | 'green';
  isLoading: boolean;
}

const accentStyles = {
  red: 'bg-swig-red/10 text-swig-red',
  navy: 'bg-swig-navy/10 text-swig-navy',
  slate: 'bg-swig-slate/20 text-swig-slate',
  green: 'bg-green-50 text-green-600',
};

function KPICard({ title, value, change, changeLabel, icon, accentColor, isLoading }: KPICardProps) {
  const changeFormatted = change !== undefined ? formatChange(change) : null;

  return (
    <div className="bg-white rounded-card shadow-card p-6 hover:shadow-card-hover transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-semibold text-swig-slate uppercase tracking-wide">{title}</p>
          {isLoading ? (
            <div className="h-9 w-28 bg-swig-card animate-pulse rounded-lg mt-2"></div>
          ) : (
            <p className="text-3xl font-display font-bold text-swig-navy mt-2">{value}</p>
          )}
          {changeFormatted && !isLoading && (
            <p className="text-sm mt-2 flex items-center gap-1">
              <span className={changeFormatted.isPositive ? 'text-green-600 font-semibold' : 'text-swig-red font-semibold'}>
                {changeFormatted.text}
              </span>
              <span className="text-swig-slate">{changeLabel}</span>
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${accentStyles[accentColor]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function KPICards({ kpis, isLoading }: KPICardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <KPICard
        title="Today's Revenue"
        value={kpis ? formatCurrency(kpis.revenue) : '$0'}
        change={kpis?.vs_yesterday.revenue}
        changeLabel="vs yesterday"
        icon={<DollarSign className="w-6 h-6" />}
        accentColor="green"
        isLoading={isLoading}
      />
      <KPICard
        title="Transactions"
        value={kpis ? kpis.transactions.toLocaleString() : '0'}
        change={kpis?.vs_yesterday.transactions}
        changeLabel="vs yesterday"
        icon={<ShoppingCart className="w-6 h-6" />}
        accentColor="navy"
        isLoading={isLoading}
      />
      <KPICard
        title="Avg Ticket"
        value={kpis ? `$${kpis.avg_ticket.toFixed(2)}` : '$0.00'}
        icon={<TrendingUp className="w-6 h-6" />}
        accentColor="red"
        isLoading={isLoading}
      />
      <KPICard
        title="Labor %"
        value={kpis ? `${kpis.labor_percentage.toFixed(1)}%` : '0%'}
        icon={<Users className="w-6 h-6" />}
        accentColor="slate"
        isLoading={isLoading}
      />
    </div>
  );
}
