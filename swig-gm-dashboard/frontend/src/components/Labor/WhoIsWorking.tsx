import { Clock, User } from 'lucide-react';
import type { Employee } from '../../types';

interface WhoIsWorkingProps {
  employees: Employee[] | undefined;
  isLoading: boolean;
}

export default function WhoIsWorking({ employees, isLoading }: WhoIsWorkingProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-card shadow-card p-6">
        <h3 className="text-lg font-display font-bold text-swig-navy mb-4">Who's Working</h3>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 bg-swig-card animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const workingNow = employees?.filter(e => e.still_working) || [];
  const minorsWorking = workingNow.filter(e => e.is_minor);

  return (
    <div className="bg-white rounded-card shadow-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-display font-bold text-swig-navy">Who's Working</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-swig-slate font-medium">
            {workingNow.length} on shift
          </span>
          {minorsWorking.length > 0 && (
            <span className="px-2.5 py-1 text-xs font-semibold bg-amber-100 text-amber-700 rounded-full">
              {minorsWorking.length} minor{minorsWorking.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {workingNow.length === 0 ? (
        <div className="text-center py-8 text-swig-slate">
          <User className="w-8 h-8 mx-auto mb-2" />
          <p>No employees currently on shift</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {workingNow.map((employee) => (
            <div
              key={employee.employee_id}
              className={`flex items-center justify-between p-3 rounded-xl border ${
                employee.is_minor ? 'bg-amber-50 border-amber-200' : 'bg-swig-card border-transparent'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                  employee.is_minor ? 'bg-amber-200' : 'bg-swig-slate/20'
                }`}>
                  <User className="w-4 h-4 text-swig-navy" />
                </div>
                <div>
                  <p className="font-semibold text-swig-navy text-sm">
                    {employee.name}
                    {employee.is_minor && (
                      <span className="ml-2 text-xs text-amber-600 font-medium">(Minor)</span>
                    )}
                  </p>
                  <p className="text-xs text-swig-slate">{employee.role}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-sm text-swig-navy font-medium">
                  <Clock className="w-3.5 h-3.5 text-swig-slate" />
                  {employee.hours_worked.toFixed(1)} hrs
                </div>
                <p className="text-xs text-swig-slate">
                  In: {employee.clock_in || '--'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
