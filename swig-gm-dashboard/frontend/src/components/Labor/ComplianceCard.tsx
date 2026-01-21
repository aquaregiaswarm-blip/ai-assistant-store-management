import { AlertTriangle, CheckCircle } from 'lucide-react';
import type { Violation } from '../../types';

interface ComplianceCardProps {
  violations: Violation[] | undefined;
  isLoading: boolean;
}

export default function ComplianceCard({ violations, isLoading }: ComplianceCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-card shadow-card p-6">
        <h3 className="text-lg font-display font-bold text-swig-navy mb-4">Compliance Violations</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-swig-card animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const unresolvedViolations = violations?.filter(v => !v.resolved) || [];
  const totalPenalty = violations?.reduce((sum, v) => sum + v.penalty_cost, 0) || 0;

  return (
    <div className="bg-white rounded-card shadow-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-display font-bold text-swig-navy">Compliance Violations</h3>
        {unresolvedViolations.length > 0 && (
          <span className="px-2.5 py-1 text-xs font-semibold bg-swig-red/10 text-swig-red rounded-full">
            {unresolvedViolations.length} unresolved
          </span>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-swig-red/10 rounded-xl p-3">
          <p className="text-xs text-swig-red font-semibold uppercase tracking-wide">Total Violations</p>
          <p className="text-2xl font-display font-bold text-swig-red">{violations?.length || 0}</p>
        </div>
        <div className="bg-amber-50 rounded-xl p-3">
          <p className="text-xs text-amber-600 font-semibold uppercase tracking-wide">Potential Penalties</p>
          <p className="text-2xl font-display font-bold text-amber-700">${totalPenalty.toFixed(0)}</p>
        </div>
      </div>

      {!violations || violations.length === 0 ? (
        <div className="text-center py-6 text-swig-slate">
          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <p>No violations in the past week</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {violations.slice(0, 5).map((violation) => (
            <div
              key={violation.violation_id}
              className={`flex items-start gap-3 p-3 rounded-xl border ${
                violation.resolved
                  ? 'bg-swig-card border-transparent'
                  : 'bg-swig-red/5 border-swig-red/20'
              }`}
            >
              <AlertTriangle className={`w-4 h-4 mt-0.5 ${
                violation.resolved ? 'text-swig-slate' : 'text-swig-red'
              }`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-swig-navy text-sm">{violation.type}</p>
                  <span className="text-xs text-swig-red font-bold">
                    ${violation.penalty_cost}
                  </span>
                </div>
                <p className="text-xs text-swig-slate mt-0.5">{violation.employee_name}</p>
                <p className="text-xs text-swig-slate/70">{violation.date}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
