import { AlertTriangle, CheckCircle } from 'lucide-react';
import type { Violation } from '../../types';

interface ComplianceCardProps {
  violations: Violation[] | undefined;
  isLoading: boolean;
}

export default function ComplianceCard({ violations, isLoading }: ComplianceCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Violations</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const unresolvedViolations = violations?.filter(v => !v.resolved) || [];
  const totalPenalty = violations?.reduce((sum, v) => sum + v.penalty_cost, 0) || 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Compliance Violations</h3>
        {unresolvedViolations.length > 0 && (
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
            {unresolvedViolations.length} unresolved
          </span>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-red-50 rounded-lg p-3">
          <p className="text-xs text-red-600 font-medium">Total Violations</p>
          <p className="text-xl font-bold text-red-700">{violations?.length || 0}</p>
        </div>
        <div className="bg-amber-50 rounded-lg p-3">
          <p className="text-xs text-amber-600 font-medium">Potential Penalties</p>
          <p className="text-xl font-bold text-amber-700">${totalPenalty.toFixed(0)}</p>
        </div>
      </div>

      {!violations || violations.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-400" />
          <p>No violations in the past week</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {violations.slice(0, 5).map((violation) => (
            <div
              key={violation.violation_id}
              className={`flex items-start gap-3 p-3 rounded-lg border ${
                violation.resolved
                  ? 'bg-gray-50 border-gray-200'
                  : 'bg-red-50 border-red-200'
              }`}
            >
              <AlertTriangle className={`w-4 h-4 mt-0.5 ${
                violation.resolved ? 'text-gray-400' : 'text-red-500'
              }`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-gray-900 text-sm">{violation.type}</p>
                  <span className="text-xs text-red-600 font-medium">
                    ${violation.penalty_cost}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mt-0.5">{violation.employee_name}</p>
                <p className="text-xs text-gray-400">{violation.date}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
