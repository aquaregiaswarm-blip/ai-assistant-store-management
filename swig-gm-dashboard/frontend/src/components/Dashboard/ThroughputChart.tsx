import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { HourlyData } from '../../types';

interface ThroughputChartProps {
  data: HourlyData[] | undefined;
  isLoading: boolean;
}

export default function ThroughputChart({ data, isLoading }: ThroughputChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Performance</h3>
        <div className="h-64 bg-gray-100 animate-pulse rounded"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Performance</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available
        </div>
      </div>
    );
  }

  // Sort by hour for display
  const sortedData = [...data].sort((a, b) => a.hour - b.hour);
  const peakHour = data.find(d => d.is_peak);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Hourly Performance</h3>
        {peakHour && (
          <span className="text-sm text-swig-pink font-medium">
            Peak: {peakHour.hour_label} ({peakHour.transactions} transactions)
          </span>
        )}
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sortedData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="hour"
              tickFormatter={(hour) => `${hour}:00`}
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickFormatter={(value) => value.toLocaleString()}
            />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === 'transactions') return [value.toLocaleString(), 'Transactions'];
                if (name === 'revenue') return [`$${value.toFixed(2)}`, 'Revenue'];
                return [value, name];
              }}
              labelFormatter={(hour) => `${hour}:00 - ${Number(hour) + 1}:00`}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
            <Bar dataKey="transactions" name="transactions" radius={[4, 4, 0, 0]}>
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.is_peak ? '#E91E63' : '#93c5fd'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
