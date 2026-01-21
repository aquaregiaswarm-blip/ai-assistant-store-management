import { CalendarDays } from 'lucide-react';
import InsightCard, { InsightItem } from './InsightCard';
import type { WeeklySummary, WeeklyComparison, WeeklyTrends } from '../../types';

interface WeekInsightsProps {
  weeklySummary: WeeklySummary | undefined;
  weeklyComparison: WeeklyComparison | undefined;
  weeklyTrends: WeeklyTrends | undefined;
  onAskAI: (question: string) => void;
  isLoading: boolean;
}

export default function WeekInsights({
  weeklySummary,
  weeklyComparison,
  weeklyTrends,
  onAskAI,
  isLoading,
}: WeekInsightsProps) {
  const items: InsightItem[] = [];

  if (isLoading) {
    return (
      <InsightCard
        title="This Week"
        icon={<CalendarDays className="w-4 h-4" />}
        items={[]}
        onAskAI={onAskAI}
        accentColor="blue"
      />
    );
  }

  // Labor percentage status
  if (weeklySummary?.labor) {
    const laborPct = weeklySummary.labor.labor_percentage;
    const targetPct = 30; // Target is <30%

    if (laborPct > targetPct) {
      items.push({
        id: 'labor-high',
        text: `Labor at ${laborPct.toFixed(1)}% - above target of ${targetPct}%`,
        question: 'Why is labor percentage high this week and how can we reduce it?',
        severity: 'warning',
      });
    } else {
      items.push({
        id: 'labor-good',
        text: `Labor at ${laborPct.toFixed(1)}% - within target`,
        question: "How's our labor cost tracking this week?",
        severity: 'info',
      });
    }
  }

  // Week over week revenue comparison
  if (weeklyComparison?.changes) {
    const revenueChange = weeklyComparison.changes.revenue;
    const changeText = revenueChange >= 0
      ? `up ${revenueChange.toFixed(1)}%`
      : `down ${Math.abs(revenueChange).toFixed(1)}%`;

    items.push({
      id: 'wow-revenue',
      text: `Revenue ${changeText} vs last week`,
      question: 'How did this week compare to last week?',
      severity: revenueChange >= 0 ? 'info' : 'warning',
    });
  }

  // Transaction trend
  if (weeklyComparison?.changes) {
    const txnChange = weeklyComparison.changes.transactions;
    const changeText = txnChange >= 0
      ? `up ${txnChange.toFixed(1)}%`
      : `down ${Math.abs(txnChange).toFixed(1)}%`;

    items.push({
      id: 'wow-transactions',
      text: `Transactions ${changeText} vs last week`,
      question: 'What are the weekly transaction trends?',
      severity: txnChange >= 0 ? 'info' : 'warning',
    });
  }

  // Best day of the week
  if (weeklyTrends?.daily && weeklyTrends.daily.length > 0) {
    const bestDay = [...weeklyTrends.daily].sort((a, b) => b.revenue - a.revenue)[0];
    items.push({
      id: 'best-day',
      text: `Best day: ${bestDay.day_name} ($${bestDay.revenue.toLocaleString()})`,
      question: "What's our best day of the week and why?",
      severity: 'info',
    });
  }

  // Compliance violations for the week
  if (weeklySummary?.compliance) {
    const violations = weeklySummary.compliance.violation_count;
    const penalties = weeklySummary.compliance.total_penalties;

    if (violations > 0) {
      items.push({
        id: 'week-violations',
        text: `${violations} violation${violations > 1 ? 's' : ''} this week ($${penalties.toFixed(0)} in penalties)`,
        question: 'What compliance issues happened this week?',
        severity: penalties > 200 ? 'critical' : 'warning',
      });
    } else {
      items.push({
        id: 'week-violations-clean',
        text: 'No compliance violations this week',
        question: 'Show me our compliance record for this week',
        severity: 'info',
      });
    }
  }

  return (
    <InsightCard
      title="This Week"
      icon={<CalendarDays className="w-4 h-4" />}
      items={items}
      onAskAI={onAskAI}
      accentColor="blue"
    />
  );
}
