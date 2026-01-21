import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { HourlyData } from '../../types';
import { getHourlyDetail } from '../../services/api';
import HourlyDetailPanel from './HourlyDetailPanel';

// Brand colors
const SWIG_RED = '#EF3D4E';
const SWIG_NAVY = '#0A1F44';
const SWIG_SLATE = '#8EA1AF';

interface ThroughputChartProps {
  data: HourlyData[] | undefined;
  isLoading: boolean;
  storeId: number;
  date: string;
}

export default function ThroughputChart({ data, isLoading, storeId, date }: ThroughputChartProps) {
  const [selectedHour, setSelectedHour] = useState<number | null>(null);

  const { data: hourlyDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['hourly-detail', storeId, selectedHour, date],
    queryFn: () => getHourlyDetail(storeId, selectedHour!, date),
    enabled: selectedHour !== null,
  });

  const handleBarClick = (data: { hour: number }) => {
    if (selectedHour === data.hour) {
      setSelectedHour(null);
    } else {
      setSelectedHour(data.hour);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-card shadow-card p-6">
        <h3 className="text-lg font-display font-bold text-swig-navy mb-4">Hourly Performance</h3>
        <div className="h-64 bg-swig-card animate-pulse rounded-lg"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-card shadow-card p-6">
        <h3 className="text-lg font-display font-bold text-swig-navy mb-4">Hourly Performance</h3>
        <div className="h-64 flex items-center justify-center text-swig-slate">
          No data available
        </div>
      </div>
    );
  }

  // Sort by hour for display
  const sortedData = [...data].sort((a, b) => a.hour - b.hour);
  const peakHour = data.find(d => d.is_peak);

  return (
    <div className="bg-white rounded-card shadow-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-display font-bold text-swig-navy">Hourly Performance</h3>
          <p className="text-sm text-swig-slate">Click a bar to see hourly details</p>
        </div>
        {peakHour && (
          <span className="text-sm text-swig-red font-semibold bg-swig-red/10 px-3 py-1 rounded-full">
            Peak: {peakHour.hour_label} ({peakHour.transactions} transactions)
          </span>
        )}
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={sortedData}
            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
            onClick={(e) => e?.activePayload?.[0]?.payload && handleBarClick(e.activePayload[0].payload)}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis
              dataKey="hour"
              tickFormatter={(hour) => `${hour}:00`}
              tick={{ fontSize: 12, fill: SWIG_SLATE }}
              stroke={SWIG_SLATE}
            />
            <YAxis
              tick={{ fontSize: 12, fill: SWIG_SLATE }}
              stroke={SWIG_SLATE}
              tickFormatter={(value) => value.toLocaleString()}
            />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === 'transactions') return [value.toLocaleString(), 'Transactions'];
                if (name === 'revenue') return [`$${value.toFixed(2)}`, 'Revenue'];
                return [value, name];
              }}
              labelFormatter={(hour) => `${hour}:00 - ${Number(hour) + 1}:00`}
              contentStyle={{
                borderRadius: '12px',
                border: 'none',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                fontFamily: 'Open Sans, sans-serif'
              }}
            />
            <Bar dataKey="transactions" name="transactions" radius={[6, 6, 0, 0]} style={{ cursor: 'pointer' }}>
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    selectedHour === entry.hour
                      ? SWIG_NAVY
                      : entry.is_peak
                      ? SWIG_RED
                      : SWIG_SLATE
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Expandable Detail Panel */}
      {selectedHour !== null && (
        <HourlyDetailPanel
          detail={hourlyDetail}
          isLoading={detailLoading}
          onClose={() => setSelectedHour(null)}
        />
      )}
    </div>
  );
}
