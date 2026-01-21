import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { Alert } from '../../types';

interface AlertBannerProps {
  alerts: Alert[] | undefined;
  isLoading: boolean;
}

function getAlertIcon(type: Alert['type']) {
  switch (type) {
    case 'high':
      return <AlertTriangle className="w-5 h-5 text-swig-red" />;
    case 'medium':
      return <AlertCircle className="w-5 h-5 text-amber-500" />;
    case 'low':
      return <Info className="w-5 h-5 text-swig-navy" />;
  }
}

function getAlertStyle(type: Alert['type']) {
  switch (type) {
    case 'high':
      return 'bg-swig-red/5 border-swig-red/20';
    case 'medium':
      return 'bg-amber-50 border-amber-200';
    case 'low':
      return 'bg-swig-navy/5 border-swig-navy/20';
  }
}

export default function AlertBanner({ alerts, isLoading }: AlertBannerProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-card shadow-card p-6">
        <h3 className="text-lg font-display font-bold text-swig-navy mb-4">Active Alerts</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-swig-card animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const sortedAlerts = alerts ? [...alerts].sort((a, b) => {
    const priority = { high: 0, medium: 1, low: 2 };
    return priority[a.type] - priority[b.type];
  }) : [];

  return (
    <div className="bg-white rounded-card shadow-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-display font-bold text-swig-navy">Active Alerts</h3>
        {sortedAlerts.length > 0 && (
          <span className="px-3 py-1 text-xs font-semibold bg-swig-red/10 text-swig-red rounded-full">
            {sortedAlerts.length} {sortedAlerts.length === 1 ? 'Alert' : 'Alerts'}
          </span>
        )}
      </div>

      {sortedAlerts.length === 0 ? (
        <div className="text-center py-8 text-swig-slate">
          <Info className="w-8 h-8 mx-auto mb-2 text-swig-slate" />
          <p>No active alerts</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {sortedAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-3 p-3 rounded-xl border ${getAlertStyle(alert.type)}`}
            >
              {getAlertIcon(alert.type)}
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-swig-navy text-sm">{alert.title}</p>
                <p className="text-sm text-swig-slate mt-0.5">{alert.description}</p>
                {alert.employee_name && (
                  <p className="text-xs text-swig-slate mt-1">Employee: {alert.employee_name}</p>
                )}
              </div>
              <span className="text-xs font-semibold text-swig-slate uppercase">{alert.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
