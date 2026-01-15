import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { Alert } from '../../types';

interface AlertBannerProps {
  alerts: Alert[] | undefined;
  isLoading: boolean;
}

function getAlertIcon(type: Alert['type']) {
  switch (type) {
    case 'high':
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    case 'medium':
      return <AlertCircle className="w-5 h-5 text-amber-500" />;
    case 'low':
      return <Info className="w-5 h-5 text-blue-500" />;
  }
}

function getAlertStyle(type: Alert['type']) {
  switch (type) {
    case 'high':
      return 'bg-red-50 border-red-200';
    case 'medium':
      return 'bg-amber-50 border-amber-200';
    case 'low':
      return 'bg-blue-50 border-blue-200';
  }
}

export default function AlertBanner({ alerts, isLoading }: AlertBannerProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 animate-pulse rounded-lg"></div>
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
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
        {sortedAlerts.length > 0 && (
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
            {sortedAlerts.length} {sortedAlerts.length === 1 ? 'Alert' : 'Alerts'}
          </span>
        )}
      </div>

      {sortedAlerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Info className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No active alerts</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {sortedAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-3 p-3 rounded-lg border ${getAlertStyle(alert.type)}`}
            >
              {getAlertIcon(alert.type)}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 text-sm">{alert.title}</p>
                <p className="text-sm text-gray-600 mt-0.5">{alert.description}</p>
                {alert.employee_name && (
                  <p className="text-xs text-gray-500 mt-1">Employee: {alert.employee_name}</p>
                )}
              </div>
              <span className="text-xs font-medium text-gray-500 uppercase">{alert.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
