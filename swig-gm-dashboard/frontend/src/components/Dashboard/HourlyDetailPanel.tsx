import type { HourlyDetail } from '../../types';

interface HourlyDetailPanelProps {
  detail: HourlyDetail | undefined;
  isLoading: boolean;
  onClose: () => void;
}

export default function HourlyDetailPanel({ detail, isLoading, onClose }: HourlyDetailPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 mt-4 animate-pulse">
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!detail) return null;

  const formatCurrency = (value: number) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  const formatTime = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mt-4 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-900">
          {detail.hour_label} Details
        </h4>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {/* Transactions */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Transactions</div>
          <div className="text-xl font-bold text-gray-900">{detail.transactions.count}</div>
          <div className="text-sm text-gray-600">{formatCurrency(detail.transactions.revenue)}</div>
        </div>

        {/* Avg Ticket */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Avg Ticket</div>
          <div className="text-xl font-bold text-gray-900">{formatCurrency(detail.transactions.avg_ticket)}</div>
        </div>

        {/* Staff Count */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Staff On Duty</div>
          <div className="text-xl font-bold text-gray-900">{detail.labor.staff_count}</div>
          <div className="text-sm text-gray-600">{formatCurrency(detail.labor.hourly_cost)}/hr</div>
        </div>

        {/* Drive-Thru Speed */}
        <div className="bg-white rounded-lg p-3 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">DT Service Time</div>
          <div className="text-xl font-bold text-gray-900">{formatTime(detail.drive_thru.avg_service_seconds)}</div>
          <div className="text-sm text-gray-600">{detail.drive_thru.cars_served} cars</div>
        </div>

        {/* Top Item */}
        {detail.top_items[0] && (
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Top Seller</div>
            <div className="text-sm font-bold text-gray-900 truncate">{detail.top_items[0].name}</div>
            <div className="text-sm text-gray-600">{detail.top_items[0].quantity} sold</div>
          </div>
        )}

        {/* Channel Mix */}
        {detail.channels.length > 0 && (
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Top Channel</div>
            <div className="text-sm font-bold text-gray-900">{detail.channels[0]?.channel.replace('_', ' ')}</div>
            <div className="text-sm text-gray-600">{detail.channels[0]?.percentage}%</div>
          </div>
        )}
      </div>

      {/* Staff List */}
      {detail.staff.length > 0 && (
        <div className="mt-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Staff Working</h5>
          <div className="flex flex-wrap gap-2">
            {detail.staff.map((s) => (
              <span
                key={s.employee_id}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {s.name} ({s.role})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Channel Breakdown */}
      {detail.channels.length > 1 && (
        <div className="mt-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Service Channels</h5>
          <div className="flex gap-4">
            {detail.channels.map((c) => (
              <div key={c.channel} className="text-sm">
                <span className="text-gray-600">{c.channel.replace('_', ' ')}:</span>{' '}
                <span className="font-medium">{c.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
