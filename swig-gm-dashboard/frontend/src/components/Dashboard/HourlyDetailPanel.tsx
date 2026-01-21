import type { HourlyDetail } from '../../types';

interface HourlyDetailPanelProps {
  detail: HourlyDetail | undefined;
  isLoading: boolean;
  onClose: () => void;
}

export default function HourlyDetailPanel({ detail, isLoading, onClose }: HourlyDetailPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-swig-card rounded-xl p-4 mt-4 animate-pulse">
        <div className="h-32 bg-white rounded-lg"></div>
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
    <div className="bg-swig-card rounded-xl p-5 mt-4 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-display font-bold text-swig-navy">
          {detail.hour_label} Details
        </h4>
        <button
          onClick={onClose}
          className="text-swig-slate hover:text-swig-navy transition-colors p-1"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {/* Transactions */}
        <div className="bg-white rounded-xl p-3 shadow-sm">
          <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">Transactions</div>
          <div className="text-xl font-display font-bold text-swig-navy">{detail.transactions.count}</div>
          <div className="text-sm text-swig-slate">{formatCurrency(detail.transactions.revenue)}</div>
        </div>

        {/* Avg Ticket */}
        <div className="bg-white rounded-xl p-3 shadow-sm">
          <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">Avg Ticket</div>
          <div className="text-xl font-display font-bold text-swig-navy">{formatCurrency(detail.transactions.avg_ticket)}</div>
        </div>

        {/* Staff Count */}
        <div className="bg-white rounded-xl p-3 shadow-sm">
          <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">Staff On Duty</div>
          <div className="text-xl font-display font-bold text-swig-navy">{detail.labor.staff_count}</div>
          <div className="text-sm text-swig-slate">{formatCurrency(detail.labor.hourly_cost)}/hr</div>
        </div>

        {/* Drive-Thru Speed */}
        <div className="bg-white rounded-xl p-3 shadow-sm">
          <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">DT Service Time</div>
          <div className="text-xl font-display font-bold text-swig-navy">{formatTime(detail.drive_thru.avg_service_seconds)}</div>
          <div className="text-sm text-swig-slate">{detail.drive_thru.cars_served} cars</div>
        </div>

        {/* Top Item */}
        {detail.top_items[0] && (
          <div className="bg-white rounded-xl p-3 shadow-sm">
            <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">Top Seller</div>
            <div className="text-sm font-bold text-swig-navy truncate">{detail.top_items[0].name}</div>
            <div className="text-sm text-swig-slate">{detail.top_items[0].quantity} sold</div>
          </div>
        )}

        {/* Channel Mix */}
        {detail.channels.length > 0 && (
          <div className="bg-white rounded-xl p-3 shadow-sm">
            <div className="text-xs text-swig-slate uppercase tracking-wide font-semibold">Top Channel</div>
            <div className="text-sm font-bold text-swig-navy">{detail.channels[0]?.channel.replace('_', ' ')}</div>
            <div className="text-sm text-swig-slate">{detail.channels[0]?.percentage}%</div>
          </div>
        )}
      </div>

      {/* Staff List */}
      {detail.staff.length > 0 && (
        <div className="mt-4">
          <h5 className="text-sm font-semibold text-swig-navy mb-2">Staff Working</h5>
          <div className="flex flex-wrap gap-2">
            {detail.staff.map((s) => (
              <span
                key={s.employee_id}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-swig-navy/10 text-swig-navy"
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
          <h5 className="text-sm font-semibold text-swig-navy mb-2">Service Channels</h5>
          <div className="flex gap-4">
            {detail.channels.map((c) => (
              <div key={c.channel} className="text-sm">
                <span className="text-swig-slate">{c.channel.replace('_', ' ')}:</span>{' '}
                <span className="font-semibold text-swig-navy">{c.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
