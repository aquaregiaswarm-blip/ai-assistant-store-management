import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { getCOGSSummary, getUsageByCategory } from '../../services/api';

interface InventoryUsageProps {
  storeId: number;
  date: string;
}

const COLORS = ['#E91E63', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#795548', '#607D8B'];

export default function InventoryUsage({ storeId, date }: InventoryUsageProps) {
  const { data: cogs, isLoading: cogsLoading } = useQuery({
    queryKey: ['cogs-summary', storeId, date],
    queryFn: () => getCOGSSummary(storeId, date),
  });

  const { data: usageByCategory, isLoading: usageLoading } = useQuery({
    queryKey: ['usage-by-category', storeId, date],
    queryFn: () => getUsageByCategory(storeId, date),
  });

  const formatCurrency = (value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

  const isLoading = cogsLoading || usageLoading;

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

  // Prepare chart data
  const cogsChartData = cogs?.by_category.map((c, i) => ({
    name: c.category,
    value: c.cost,
    color: COLORS[i % COLORS.length],
  })) || [];

  const categoryBarData = usageByCategory?.map((c) => ({
    category: c.category.length > 12 ? c.category.substring(0, 12) + '...' : c.category,
    cost: c.total_cost,
    items: c.item_count,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Total Revenue</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(cogs?.total_revenue || 0)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Total COGS</div>
          <div className="text-2xl font-bold text-red-600">{formatCurrency(cogs?.total_cogs || 0)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">COGS %</div>
          <div className={`text-2xl font-bold ${(cogs?.cogs_percentage || 0) > 30 ? 'text-red-600' : 'text-green-600'}`}>
            {cogs?.cogs_percentage || 0}%
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Gross Profit</div>
          <div className="text-2xl font-bold text-green-600">{formatCurrency(cogs?.gross_profit || 0)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Gross Margin</div>
          <div className="text-2xl font-bold text-gray-900">{cogs?.gross_margin || 0}%</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Categories Used</div>
          <div className="text-2xl font-bold text-gray-900">{cogs?.by_category.length || 0}</div>
        </div>
      </div>

      {/* COGS Breakdown Visual */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown Visualization</h3>
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 items-center">
          {/* Revenue Bar */}
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">Revenue</div>
            <div className="h-32 bg-green-500 rounded-lg flex items-end justify-center">
              <span className="text-white font-bold pb-2">{formatCurrency(cogs?.total_revenue || 0)}</span>
            </div>
          </div>
          {/* Arrow */}
          <div className="hidden lg:flex justify-center items-center text-gray-400">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
          {/* COGS Bar */}
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">COGS ({cogs?.cogs_percentage}%)</div>
            <div
              className="bg-red-500 rounded-lg flex items-end justify-center"
              style={{ height: `${Math.max(20, (cogs?.cogs_percentage || 0) * 1.28)}px` }}
            >
              <span className="text-white font-bold pb-2 text-sm">{formatCurrency(cogs?.total_cogs || 0)}</span>
            </div>
          </div>
          {/* Arrow */}
          <div className="hidden lg:flex justify-center items-center text-gray-400">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
          {/* Profit Bar */}
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-2">Gross Profit ({cogs?.gross_margin}%)</div>
            <div
              className="bg-blue-500 rounded-lg flex items-end justify-center"
              style={{ height: `${Math.max(20, (cogs?.gross_margin || 0) * 1.28)}px` }}
            >
              <span className="text-white font-bold pb-2 text-sm">{formatCurrency(cogs?.gross_profit || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* COGS by Category Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">COGS by Ingredient Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={cogsChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {cogsChartData.map((entry, index) => (
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

        {/* Category Cost Bar Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost by Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryBarData} layout="vertical" margin={{ left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tickFormatter={(v) => `$${v}`} />
                <YAxis type="category" dataKey="category" tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Bar dataKey="cost" fill="#E91E63" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Category Breakdown Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">COGS Breakdown by Category</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cost</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">% of COGS</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {cogs?.by_category.map((cat, i) => (
                <tr key={cat.category}>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                      <span className="text-sm font-medium text-gray-900">{cat.category}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                    {formatCurrency(cat.cost)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-600">
                    {cat.percentage}%
                  </td>
                </tr>
              ))}
              <tr className="bg-gray-50 font-semibold">
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">Total</td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatCurrency(cogs?.total_cogs || 0)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-gray-900">100%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Items by Category */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Ingredient Usage Details</h3>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {usageByCategory?.map((category) => (
            <div key={category.category} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">{category.category}</h4>
                <span className="text-sm font-medium text-swig-pink">{formatCurrency(category.total_cost)}</span>
              </div>
              <div className="text-xs text-gray-500 mb-2">{category.item_count} items used</div>
              <div className="space-y-2">
                {category.top_items.slice(0, 3).map((item, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className="text-gray-600 truncate mr-2">{item.name}</span>
                    <span className="text-gray-900 font-medium whitespace-nowrap">{formatCurrency(item.cost)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
