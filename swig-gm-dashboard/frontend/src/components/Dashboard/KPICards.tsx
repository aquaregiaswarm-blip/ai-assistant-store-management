import { DollarSign, ShoppingCart, Users } from 'lucide-react';
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

function formatChange(value: number): { text: string; color: string } {
  const sign = value >= 0 ? '+' : '';
  const color = value >= 0 ? 'text-green-600' : 'text-red-600';
  return { text: `${sign}${value.toFixed(1)}%`, color };
}

interface KPICardProps {
  title: string;
  value: string;
  change?: number;
  changeLabel?: string;
  icon: React.ReactNode;
  iconBgColor: string;
  isLoading: boolean;
}

function KPICard({ title, value, change, changeLabel, icon, iconBgColor, isLoading }: KPICardProps) {
  const changeFormatted = change !== undefined ? formatChange(change) : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          {isLoading ? (
            <div className="h-8 w-24 bg-gray-200 animate-pulse rounded mt-1"></div>
          ) : (
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          )}
          {changeFormatted && !isLoading && (
            <p className={`text-sm mt-1 ${changeFormatted.color}`}>
              {changeFormatted.text} <span className="text-gray-400">{changeLabel}</span>
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${iconBgColor}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function KPICards({ kpis, isLoading }: KPICardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Today's Revenue"
        value={kpis ? formatCurrency(kpis.revenue) : '$0'}
        change={kpis?.vs_yesterday.revenue}
        changeLabel="vs yesterday"
        icon={<DollarSign className="w-6 h-6 text-green-600" />}
        iconBgColor="bg-green-50"
        isLoading={isLoading}
      />
      <KPICard
        title="Transactions"
        value={kpis ? kpis.transactions.toLocaleString() : '0'}
        change={kpis?.vs_yesterday.transactions}
        changeLabel="vs yesterday"
        icon={<ShoppingCart className="w-6 h-6 text-blue-600" />}
        iconBgColor="bg-blue-50"
        isLoading={isLoading}
      />
      <KPICard
        title="Avg Ticket"
        value={kpis ? `$${kpis.avg_ticket.toFixed(2)}` : '$0.00'}
        icon={<DollarSign className="w-6 h-6 text-purple-600" />}
        iconBgColor="bg-purple-50"
        isLoading={isLoading}
      />
      <KPICard
        title="Labor %"
        value={kpis ? `${kpis.labor_percentage.toFixed(1)}%` : '0%'}
        icon={<Users className="w-6 h-6 text-orange-600" />}
        iconBgColor="bg-orange-50"
        isLoading={isLoading}
      />
    </div>
  );
}
