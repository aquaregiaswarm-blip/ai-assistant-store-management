import { Clock, User } from 'lucide-react';
import type { Employee } from '../../types';

interface WhoIsWorkingProps {
  employees: Employee[] | undefined;
  isLoading: boolean;
}

export default function WhoIsWorking({ employees, isLoading }: WhoIsWorkingProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Who's Working</h3>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 bg-gray-100 animate-pulse rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const workingNow = employees?.filter(e => e.still_working) || [];
  const minorsWorking = workingNow.filter(e => e.is_minor);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Who's Working</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {workingNow.length} on shift
          </span>
          {minorsWorking.length > 0 && (
            <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">
              {minorsWorking.length} minor{minorsWorking.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {workingNow.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <User className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No employees currently on shift</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {workingNow.map((employee) => (
            <div
              key={employee.employee_id}
              className={`flex items-center justify-between p-3 rounded-lg border ${
                employee.is_minor ? 'bg-amber-50 border-amber-200' : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  employee.is_minor ? 'bg-amber-200' : 'bg-gray-200'
                }`}>
                  <User className="w-4 h-4 text-gray-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900 text-sm">
                    {employee.name}
                    {employee.is_minor && (
                      <span className="ml-2 text-xs text-amber-600">(Minor)</span>
                    )}
                  </p>
                  <p className="text-xs text-gray-500">{employee.role}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Clock className="w-3 h-3" />
                  {employee.hours_worked.toFixed(1)} hrs
                </div>
                <p className="text-xs text-gray-400">
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
