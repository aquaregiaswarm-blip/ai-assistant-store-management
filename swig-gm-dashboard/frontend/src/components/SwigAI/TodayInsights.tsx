import { Calendar } from 'lucide-react';
import InsightCard, { InsightItem } from './InsightCard';
import type { RosterData, Violation, KPIs } from '../../types';

interface TodayInsightsProps {
  roster: RosterData | undefined;
  violations: Violation[] | undefined;
  kpis: KPIs | undefined;
  onAskAI: (question: string) => void;
  isLoading: boolean;
}

export default function TodayInsights({
  roster,
  violations,
  kpis,
  onAskAI,
  isLoading,
}: TodayInsightsProps) {
  const items: InsightItem[] = [];

  if (isLoading) {
    return (
      <InsightCard
        title="Today"
        icon={<Calendar className="w-4 h-4" />}
        items={[]}
        onAskAI={onAskAI}
        accentColor="orange"
      />
    );
  }

  // Late arrivals
  if (roster?.summary.late_arrivals && roster.summary.late_arrivals > 0) {
    items.push({
      id: 'late-arrivals',
      text: `${roster.summary.late_arrivals} late arrival${roster.summary.late_arrivals > 1 ? 's' : ''} today`,
      question: 'Who arrived late today and by how much?',
      severity: 'warning',
    });
  }

  // No shows
  if (roster?.summary.no_shows && roster.summary.no_shows > 0) {
    items.push({
      id: 'no-shows',
      text: `${roster.summary.no_shows} no-show${roster.summary.no_shows > 1 ? 's' : ''} today`,
      question: 'Who were the no-shows today and what shifts were affected?',
      severity: 'critical',
    });
  }

  // Overtime risk - check roster for people approaching high hours
  const overtimeRisk = roster?.roster.filter(
    (emp) => emp.actual.hours >= 8 && emp.actual.hours < 10
  ) || [];

  if (overtimeRisk.length > 0) {
    items.push({
      id: 'overtime-risk',
      text: `${overtimeRisk.length} employee${overtimeRisk.length > 1 ? 's' : ''} approaching overtime (${overtimeRisk.slice(0, 2).map(e => e.name.split(' ')[0]).join(', ')}${overtimeRisk.length > 2 ? '...' : ''})`,
      question: 'Which employees are approaching overtime this week?',
      severity: 'warning',
    });
  }

  // Today's violations
  const todayViolations = violations?.filter(
    (v) => !v.resolved
  ) || [];

  if (todayViolations.length > 0) {
    const totalPenalties = todayViolations.reduce((sum, v) => sum + v.penalty_cost, 0);
    items.push({
      id: 'violations-today',
      text: `${todayViolations.length} unresolved violation${todayViolations.length > 1 ? 's' : ''} ($${totalPenalties.toFixed(0)} in penalties)`,
      question: 'What compliance violations need attention today?',
      severity: totalPenalties > 100 ? 'critical' : 'warning',
    });
  }

  // Revenue pace vs yesterday
  if (kpis?.vs_yesterday.revenue) {
    const paceText = kpis.vs_yesterday.revenue >= 0
      ? `up ${kpis.vs_yesterday.revenue.toFixed(1)}%`
      : `down ${Math.abs(kpis.vs_yesterday.revenue).toFixed(1)}%`;

    items.push({
      id: 'revenue-pace',
      text: `Revenue ${paceText} vs yesterday`,
      question: 'How is our revenue tracking compared to yesterday?',
      severity: kpis.vs_yesterday.revenue >= 0 ? 'info' : 'warning',
    });
  }

  // Break violations
  if (roster?.summary.break_violations && roster.summary.break_violations > 0) {
    items.push({
      id: 'break-violations',
      text: `${roster.summary.break_violations} break violation${roster.summary.break_violations > 1 ? 's' : ''} today`,
      question: 'Show me break violations from today',
      severity: 'warning',
    });
  }

  return (
    <InsightCard
      title="Today"
      icon={<Calendar className="w-4 h-4" />}
      items={items}
      onAskAI={onAskAI}
      accentColor="orange"
    />
  );
}
