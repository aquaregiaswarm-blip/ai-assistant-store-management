import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { getSalesByCategory, getPaymentBreakdown, getLoyaltyStats, getTopItems } from '../../services/api';

interface SalesSummaryProps {
  storeId: number;
  date: string;
}

const COLORS = ['#E91E63', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#795548', '#607D8B'];

export default function SalesSummary({ storeId, date }: SalesSummaryProps) {
  const { data: salesByCategory, isLoading: categoryLoading } = useQuery({
    queryKey: ['sales-by-category', storeId, date],
    queryFn: () => getSalesByCategory(storeId, date),
  });

  const { data: payments, isLoading: paymentsLoading } = useQuery({
    queryKey: ['payment-breakdown', storeId, date],
    queryFn: () => getPaymentBreakdown(storeId, date),
  });

  const { data: loyalty, isLoading: loyaltyLoading } = useQuery({
    queryKey: ['loyalty-stats', storeId, date],
    queryFn: () => getLoyaltyStats(storeId, date),
  });

  const { data: topItems, isLoading: topItemsLoading } = useQuery({
    queryKey: ['top-items', storeId, date],
    queryFn: () => getTopItems(storeId, date, 10),
  });

  const formatCurrency = (value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

  const isLoading = categoryLoading || paymentsLoading || loyaltyLoading || topItemsLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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

  // Prepare pie chart data
  const categoryData = salesByCategory?.by_category.map((c, i) => ({
    name: c.category,
    value: c.revenue,
    color: COLORS[i % COLORS.length],
  })) || [];

  const paymentData = payments?.by_method.map((p, i) => ({
    name: p.method.replace('_', ' '),
    value: p.transaction_count,
    color: COLORS[i % COLORS.length],
  })) || [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Total Revenue</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(salesByCategory?.total_revenue || 0)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Transactions</div>
          <div className="text-2xl font-bold text-gray-900">{payments?.summary.total_transactions || 0}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Total Tips</div>
          <div className="text-2xl font-bold text-green-600">{formatCurrency(payments?.summary.total_tips || 0)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Tip %</div>
          <div className="text-2xl font-bold text-gray-900">{payments?.summary.tip_percentage || 0}%</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Loyalty Members</div>
          <div className="text-2xl font-bold text-swig-pink">{loyalty?.loyalty.transactions || 0}</div>
          <div className="text-sm text-gray-500">{loyalty?.loyalty.percentage}% of orders</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Loyalty Avg Ticket</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(loyalty?.loyalty.avg_ticket || 0)}</div>
          <div className="text-sm text-gray-500">vs {formatCurrency(loyalty?.non_loyalty.avg_ticket || 0)} non-loyalty</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales by Category */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sales by Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Methods</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={paymentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {paymentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => `${value} transactions`}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Items */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Top Selling Items</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Revenue</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topItems?.map((item) => (
                  <tr key={item.rank}>
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-500">{item.rank}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{item.item_name}</div>
                      <div className="text-xs text-gray-500">{item.item_type}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-900">{item.quantity_sold}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(item.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category Breakdown Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900">Category Breakdown</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Orders</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">%</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {salesByCategory?.by_category.map((cat, i) => (
                  <tr key={cat.category}>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                        <span className="text-sm font-medium text-gray-900">{cat.category}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{cat.transaction_count}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{cat.quantity_sold}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(cat.revenue)}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{cat.percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Payment Details Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Payment Method Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Transactions</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">%</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tips</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Amount</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {payments?.by_method.map((pm) => (
                <tr key={pm.method}>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{pm.method.replace('_', ' ')}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{pm.transaction_count}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{pm.percentage}%</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">{formatCurrency(pm.total_amount)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-green-600">{formatCurrency(pm.tips)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">{formatCurrency(pm.avg_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
