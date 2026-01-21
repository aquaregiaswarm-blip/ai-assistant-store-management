import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { getWeeklySummary, getWeeklyTrends, getWeeklyComparison } from '../../services/api';

interface WeeklySummaryProps {
  storeId: number;
  date: string;
}

export default function WeeklySummaryView({ storeId, date }: WeeklySummaryProps) {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['weekly-summary', storeId, date],
    queryFn: () => getWeeklySummary(storeId, date),
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['weekly-trends', storeId, date],
    queryFn: () => getWeeklyTrends(storeId, date),
  });

  const { data: comparison, isLoading: comparisonLoading } = useQuery({
    queryKey: ['weekly-comparison', storeId, date],
    queryFn: () => getWeeklyComparison(storeId, date),
  });

  const formatCurrency = (value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const isLoading = summaryLoading || trendsLoading || comparisonLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const changeColor = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const changeIcon = (value: number) => {
    if (value > 0) return '↑';
    if (value < 0) return '↓';
    return '→';
  };

  return (
    <div className="space-y-6">
      {/* Week Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Week of {formatDate(summary?.week_start || '')}</h2>
            <p className="text-sm text-gray-500">{formatDate(summary?.week_start || '')} - {formatDate(summary?.week_end || '')}</p>
          </div>
          {comparison && (
            <div className="text-right">
              <div className="text-sm text-gray-500">vs Previous Week</div>
              <div className={`text-lg font-bold ${changeColor(comparison.changes.revenue)}`}>
                {changeIcon(comparison.changes.revenue)} {Math.abs(comparison.changes.revenue)}% Revenue
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Total Revenue</div>
          <div className="text-xl font-bold text-gray-900">{formatCurrency(summary?.sales.total_revenue || 0)}</div>
          {comparison && (
            <div className={`text-xs ${changeColor(comparison.changes.revenue)}`}>
              {changeIcon(comparison.changes.revenue)} {Math.abs(comparison.changes.revenue)}%
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Transactions</div>
          <div className="text-xl font-bold text-gray-900">{summary?.sales.transaction_count || 0}</div>
          {comparison && (
            <div className={`text-xs ${changeColor(comparison.changes.transactions)}`}>
              {changeIcon(comparison.changes.transactions)} {Math.abs(comparison.changes.transactions)}%
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Avg Ticket</div>
          <div className="text-xl font-bold text-gray-900">{formatCurrency(summary?.sales.avg_ticket || 0)}</div>
          {comparison && (
            <div className={`text-xs ${changeColor(comparison.changes.avg_ticket)}`}>
              {changeIcon(comparison.changes.avg_ticket)} {Math.abs(comparison.changes.avg_ticket)}%
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Loyalty %</div>
          <div className="text-xl font-bold text-swig-pink">{summary?.sales.loyalty_percentage || 0}%</div>
          <div className="text-xs text-gray-500">{summary?.sales.loyalty_transactions} members</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Labor Hours</div>
          <div className="text-xl font-bold text-gray-900">{summary?.labor.total_hours || 0}</div>
          <div className="text-xs text-gray-500">{summary?.labor.employees_worked} employees</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Labor Cost</div>
          <div className="text-xl font-bold text-gray-900">{formatCurrency(summary?.labor.total_cost || 0)}</div>
          {comparison && (
            <div className={`text-xs ${changeColor(-comparison.changes.labor_cost)}`}>
              {changeIcon(-comparison.changes.labor_cost)} {Math.abs(comparison.changes.labor_cost)}%
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Labor %</div>
          <div className={`text-xl font-bold ${(summary?.labor.labor_percentage || 0) > 25 ? 'text-red-600' : 'text-green-600'}`}>
            {summary?.labor.labor_percentage || 0}%
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Violations</div>
          <div className={`text-xl font-bold ${(summary?.compliance.violation_count || 0) > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {summary?.compliance.violation_count || 0}
          </div>
          <div className="text-xs text-gray-500">{formatCurrency(summary?.compliance.total_penalties || 0)} penalties</div>
        </div>
      </div>

      {/* Revenue Trend Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Revenue Trend</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends?.daily || []} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="day_name"
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => v.substring(0, 3)}
              />
              <YAxis
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'revenue') return [formatCurrency(value), 'Revenue'];
                  if (name === 'labor_cost') return [formatCurrency(value), 'Labor Cost'];
                  return [value, name];
                }}
                labelFormatter={(label) => label}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              />
              <Legend />
              <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#E91E63" strokeWidth={3} dot={{ fill: '#E91E63' }} />
              <Line type="monotone" dataKey="labor_cost" name="Labor Cost" stroke="#2196F3" strokeWidth={2} dot={{ fill: '#2196F3' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Transaction Trend and Labor % */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transactions Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Transactions</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends?.daily || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="day_name"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(v) => v.substring(0, 3)}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), 'Transactions']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Bar dataKey="transactions" fill="#E91E63" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Labor % Trend */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Labor %</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends?.daily || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="day_name"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(v) => v.substring(0, 3)}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  domain={[0, 'auto']}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  formatter={(value: number) => [`${value}%`, 'Labor %']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Line
                  type="monotone"
                  dataKey="labor_percentage"
                  stroke="#4CAF50"
                  strokeWidth={3}
                  dot={{ fill: '#4CAF50' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Week over Week Comparison */}
      {comparison && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Week-over-Week Comparison</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Metric</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Previous Week<br/>
                    <span className="text-xs font-normal normal-case">{formatDate(comparison.previous_week.start)} - {formatDate(comparison.previous_week.end)}</span>
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Current Week<br/>
                    <span className="text-xs font-normal normal-case">{formatDate(comparison.current_week.start)} - {formatDate(comparison.current_week.end)}</span>
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Change</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">Revenue</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{formatCurrency(comparison.previous_week.revenue)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(comparison.current_week.revenue)}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-bold ${changeColor(comparison.changes.revenue)}`}>
                    {changeIcon(comparison.changes.revenue)} {Math.abs(comparison.changes.revenue)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">Transactions</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{comparison.previous_week.transactions.toLocaleString()}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{comparison.current_week.transactions.toLocaleString()}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-bold ${changeColor(comparison.changes.transactions)}`}>
                    {changeIcon(comparison.changes.transactions)} {Math.abs(comparison.changes.transactions)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">Avg Ticket</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{formatCurrency(comparison.previous_week.avg_ticket)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(comparison.current_week.avg_ticket)}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-bold ${changeColor(comparison.changes.avg_ticket)}`}>
                    {changeIcon(comparison.changes.avg_ticket)} {Math.abs(comparison.changes.avg_ticket)}%
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">Labor Cost</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{formatCurrency(comparison.previous_week.labor_cost)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(comparison.current_week.labor_cost)}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-bold ${changeColor(-comparison.changes.labor_cost)}`}>
                    {changeIcon(comparison.changes.labor_cost)} {Math.abs(comparison.changes.labor_cost)}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Items for the Week */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Top Sellers This Week</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {summary?.top_items.map((item, i) => (
              <div key={i} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-swig-pink mb-1">#{i + 1}</div>
                <div className="text-sm font-medium text-gray-900 mb-1">{item.name}</div>
                <div className="text-xs text-gray-500">{item.quantity} sold</div>
                <div className="text-xs text-gray-500">{formatCurrency(item.revenue)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
