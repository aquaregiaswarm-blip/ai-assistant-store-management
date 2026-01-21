import { useQuery } from '@tanstack/react-query';
import RightNowInsights from './RightNowInsights';
import TodayInsights from './TodayInsights';
import WeekInsights from './WeekInsights';
import PlanningInsights from './PlanningInsights';
import {
  getWhosWorking,
  getHourlyData,
  getKPIs,
  getRoster,
  getViolations,
  getWeeklySummary,
  getWeeklyComparison,
  getWeeklyTrends,
  getTopItems,
  getCOGSSummary,
  getLoyaltyStats,
} from '../../services/api';

interface InsightsPanelProps {
  storeId: number;
  date: string;
  onAskAI: (question: string) => void;
}

export default function InsightsPanel({ storeId, date, onAskAI }: InsightsPanelProps) {
  // Real-time data
  const { data: employees, isLoading: employeesLoading } = useQuery({
    queryKey: ['whos-working', storeId, date],
    queryFn: () => getWhosWorking(storeId, date),
  });

  const { data: hourlyData, isLoading: hourlyLoading } = useQuery({
    queryKey: ['hourly', storeId, date],
    queryFn: () => getHourlyData(storeId, date),
  });

  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis', storeId, date],
    queryFn: () => getKPIs(storeId, date),
  });

  // Today data
  const { data: roster, isLoading: rosterLoading } = useQuery({
    queryKey: ['roster', storeId, date],
    queryFn: () => getRoster(storeId, date),
  });

  const { data: violations, isLoading: violationsLoading } = useQuery({
    queryKey: ['violations', storeId, date],
    queryFn: () => getViolations(storeId, 7, date),
  });

  // Weekly data
  const { data: weeklySummary, isLoading: weeklySummaryLoading } = useQuery({
    queryKey: ['weekly-summary', storeId, date],
    queryFn: () => getWeeklySummary(storeId, date),
  });

  const { data: weeklyComparison, isLoading: weeklyComparisonLoading } = useQuery({
    queryKey: ['weekly-comparison', storeId, date],
    queryFn: () => getWeeklyComparison(storeId, date),
  });

  const { data: weeklyTrends, isLoading: weeklyTrendsLoading } = useQuery({
    queryKey: ['weekly-trends', storeId, date],
    queryFn: () => getWeeklyTrends(storeId, date),
  });

  // Planning data
  const { data: topItems, isLoading: topItemsLoading } = useQuery({
    queryKey: ['top-items', storeId, date],
    queryFn: () => getTopItems(storeId, date, 5),
  });

  const { data: cogsSummary, isLoading: cogsLoading } = useQuery({
    queryKey: ['cogs', storeId, date],
    queryFn: () => getCOGSSummary(storeId, date),
  });

  const { data: loyaltyStats, isLoading: loyaltyLoading } = useQuery({
    queryKey: ['loyalty', storeId, date],
    queryFn: () => getLoyaltyStats(storeId, date),
  });

  const rightNowLoading = employeesLoading || hourlyLoading || kpisLoading;
  const todayLoading = rosterLoading || violationsLoading || kpisLoading;
  const weekLoading = weeklySummaryLoading || weeklyComparisonLoading || weeklyTrendsLoading;
  const planningLoading = topItemsLoading || cogsLoading || loyaltyLoading || weeklySummaryLoading;

  return (
    <div className="h-full overflow-y-auto pr-2 space-y-4">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-swig-navy">What's Next</h2>
        <p className="text-sm text-gray-500">Click any insight to ask SwigAI for details</p>
      </div>

      <RightNowInsights
        employees={employees}
        hourlyData={hourlyData}
        kpis={kpis}
        onAskAI={onAskAI}
        isLoading={rightNowLoading}
      />

      <TodayInsights
        roster={roster}
        violations={violations}
        kpis={kpis}
        onAskAI={onAskAI}
        isLoading={todayLoading}
      />

      <WeekInsights
        weeklySummary={weeklySummary}
        weeklyComparison={weeklyComparison}
        weeklyTrends={weeklyTrends}
        onAskAI={onAskAI}
        isLoading={weekLoading}
      />

      <PlanningInsights
        topItems={topItems}
        cogsSummary={cogsSummary}
        weeklySummary={weeklySummary}
        loyaltyStats={loyaltyStats}
        onAskAI={onAskAI}
        isLoading={planningLoading}
      />
    </div>
  );
}
