import { useQuery } from '@tanstack/react-query';
import { getRoster } from '../../services/api';

interface DailyRosterProps {
  storeId: number;
  date: string;
}

const roleColors: Record<string, string> = {
  GM: 'bg-purple-100 text-purple-800',
  ASM: 'bg-blue-100 text-blue-800',
  SHIFT: 'bg-green-100 text-green-800',
  MIX: 'bg-yellow-100 text-yellow-800',
  RUNNER: 'bg-orange-100 text-orange-800',
  TRAIN: 'bg-gray-100 text-gray-800',
};

export default function DailyRoster({ storeId, date }: DailyRosterProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['roster', storeId, date],
    queryFn: () => getRoster(storeId, date),
  });

  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return '-';
    const time = new Date(timestamp);
    return time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Employees</div>
          <div className="text-2xl font-bold text-gray-900">{data.summary.employee_count}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Scheduled Hrs</div>
          <div className="text-2xl font-bold text-gray-900">{data.summary.total_scheduled_hours}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Actual Hrs</div>
          <div className="text-2xl font-bold text-gray-900">{data.summary.total_actual_hours}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Variance</div>
          <div className={`text-2xl font-bold ${data.summary.hours_variance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {data.summary.hours_variance >= 0 ? '+' : ''}{data.summary.hours_variance}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Labor Cost</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(data.summary.total_labor_cost)}</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Late Arrivals</div>
          <div className={`text-2xl font-bold ${data.summary.late_arrivals > 0 ? 'text-yellow-600' : 'text-gray-900'}`}>
            {data.summary.late_arrivals}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">No Shows</div>
          <div className={`text-2xl font-bold ${data.summary.no_shows > 0 ? 'text-red-600' : 'text-gray-900'}`}>
            {data.summary.no_shows}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wide">Break Issues</div>
          <div className={`text-2xl font-bold ${data.summary.break_violations > 0 ? 'text-red-600' : 'text-gray-900'}`}>
            {data.summary.break_violations}
          </div>
        </div>
      </div>

      {/* Role Distribution */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h3 className="text-sm font-display font-semibold text-swig-navy mb-3">Role Distribution</h3>
        <div className="flex flex-wrap gap-3">
          {data.role_distribution.map((r) => (
            <div key={r.role} className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${roleColors[r.role] || 'bg-gray-100 text-gray-800'}`}>
                {r.role}
              </span>
              <span className="text-sm text-gray-600">{r.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Roster Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-display font-bold text-swig-navy">Employee Roster</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scheduled</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Hours</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Break</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Labor Cost</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.roster.map((employee) => (
                <tr key={employee.employee_id} className={employee.attendance.is_no_show ? 'bg-red-50' : ''}>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{employee.name}</div>
                        {employee.is_minor && (
                          <span className="inline-flex px-1.5 py-0.5 text-xs rounded bg-yellow-100 text-yellow-800">Minor</span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${roleColors[employee.role] || 'bg-gray-100 text-gray-800'}`}>
                      {employee.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    <div>{formatTime(employee.schedule.start)} - {formatTime(employee.schedule.end)}</div>
                    <div className="text-xs text-gray-400">{employee.schedule.hours}h</div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                    <div>{formatTime(employee.actual.clock_in)} - {formatTime(employee.actual.clock_out)}</div>
                    <div className="text-xs text-gray-400">{employee.actual.hours}h</div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center text-sm font-medium text-gray-900">
                    {employee.actual.hours}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className={`text-sm font-medium ${
                      employee.variance > 0 ? 'text-green-600' : employee.variance < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {employee.variance > 0 ? '+' : ''}{employee.variance}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    {employee.break.taken ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        {employee.break.duration_minutes}m
                      </span>
                    ) : employee.actual.hours >= 5 ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        Missing
                      </span>
                    ) : (
                      <span className="text-xs text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                    {formatCurrency(employee.labor_cost)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <div className="flex flex-col items-center gap-1">
                      {employee.attendance.is_no_show && (
                        <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">No Show</span>
                      )}
                      {employee.attendance.is_late && (
                        <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          Late {employee.attendance.late_minutes}m
                        </span>
                      )}
                      {employee.violations.length > 0 && (
                        <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                          {employee.violations.length} violation{employee.violations.length > 1 ? 's' : ''}
                        </span>
                      )}
                      {!employee.attendance.is_no_show && !employee.attendance.is_late && employee.violations.length === 0 && (
                        <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">OK</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
