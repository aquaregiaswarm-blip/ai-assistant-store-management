import { Flame } from 'lucide-react';
import InsightCard, { InsightItem } from './InsightCard';
import type { Employee, HourlyData, KPIs } from '../../types';

interface RightNowInsightsProps {
  employees: Employee[] | undefined;
  hourlyData: HourlyData[] | undefined;
  kpis: KPIs | undefined;
  onAskAI: (question: string) => void;
  isLoading: boolean;
}

export default function RightNowInsights({
  employees,
  hourlyData,
  kpis,
  onAskAI,
  isLoading,
}: RightNowInsightsProps) {
  const items: InsightItem[] = [];

  if (isLoading) {
    return (
      <InsightCard
        title="Right Now"
        icon={<Flame className="w-4 h-4" />}
        items={[]}
        onAskAI={onAskAI}
        accentColor="red"
      />
    );
  }

  // Check for minors needing breaks (approaching 3.5 hours)
  const minorsWorking = employees?.filter(
    (emp) => emp.is_minor && emp.still_working
  ) || [];

  const minorsNeedingBreaks = minorsWorking.filter(
    (emp) => emp.hours_worked >= 3.0 && emp.hours_worked < 4.0
  );

  if (minorsNeedingBreaks.length > 0) {
    items.push({
      id: 'minor-breaks',
      text: `${minorsNeedingBreaks.length} minor${minorsNeedingBreaks.length > 1 ? 's' : ''} ${minorsNeedingBreaks.length > 1 ? 'need' : 'needs'} a break soon (${minorsNeedingBreaks.map(m => m.first_name).join(', ')})`,
      question: 'Which minors are working and when do they need breaks?',
      severity: 'warning',
    });
  }

  // Check for peak hour approaching (next 1-2 hours)
  const currentHour = new Date().getHours();
  const peakHours = hourlyData?.filter((h) => h.is_peak) || [];
  const upcomingPeak = peakHours.find(
    (h) => h.hour > currentHour && h.hour <= currentHour + 2
  );

  if (upcomingPeak) {
    items.push({
      id: 'peak-hour',
      text: `Peak hour expected at ${upcomingPeak.hour_label}`,
      question: 'What are our peak hours and how should I prepare?',
      severity: 'info',
    });
  }

  // Current throughput status
  if (kpis) {
    const throughputTarget = 100; // Target cars/hour
    if (kpis.throughput >= throughputTarget) {
      items.push({
        id: 'throughput-good',
        text: `Throughput at ${kpis.throughput.toFixed(0)} cars/hr - hitting target`,
        question: 'How is our drive-thru performance right now?',
        severity: 'info',
      });
    } else if (kpis.throughput > 0 && kpis.throughput < throughputTarget * 0.8) {
      items.push({
        id: 'throughput-low',
        text: `Throughput at ${kpis.throughput.toFixed(0)} cars/hr - below target of ${throughputTarget}`,
        question: 'Why is our throughput low and how can we improve it?',
        severity: 'warning',
      });
    }
  }

  // Staff on floor count
  const stillWorking = employees?.filter((emp) => emp.still_working) || [];
  if (stillWorking.length > 0) {
    const roleBreakdown = stillWorking.reduce((acc, emp) => {
      acc[emp.role] = (acc[emp.role] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const rolesText = Object.entries(roleBreakdown)
      .map(([role, count]) => `${count} ${role}`)
      .join(', ');

    items.push({
      id: 'staff-count',
      text: `${stillWorking.length} staff on floor (${rolesText})`,
      question: "Who's currently working and what roles are covered?",
      severity: 'info',
    });
  }

  return (
    <InsightCard
      title="Right Now"
      icon={<Flame className="w-4 h-4" />}
      items={items}
      onAskAI={onAskAI}
      accentColor="red"
    />
  );
}
