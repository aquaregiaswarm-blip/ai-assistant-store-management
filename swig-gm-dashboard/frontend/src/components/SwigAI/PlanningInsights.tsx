import { Target } from 'lucide-react';
import InsightCard, { InsightItem } from './InsightCard';
import type { TopItem, COGSSummary, WeeklySummary, LoyaltyStats } from '../../types';

interface PlanningInsightsProps {
  topItems: TopItem[] | undefined;
  cogsSummary: COGSSummary | undefined;
  weeklySummary: WeeklySummary | undefined;
  loyaltyStats: LoyaltyStats | undefined;
  onAskAI: (question: string) => void;
  isLoading: boolean;
}

export default function PlanningInsights({
  topItems,
  cogsSummary,
  weeklySummary,
  loyaltyStats,
  onAskAI,
  isLoading,
}: PlanningInsightsProps) {
  const items: InsightItem[] = [];

  if (isLoading) {
    return (
      <InsightCard
        title="Planning Ahead"
        icon={<Target className="w-4 h-4" />}
        items={[]}
        onAskAI={onAskAI}
        accentColor="green"
      />
    );
  }

  // Top sellers to stock
  if (topItems && topItems.length > 0) {
    const topSellers = topItems.slice(0, 3).map(item => item.item_name.split(' ')[0]).join(', ');
    items.push({
      id: 'top-sellers',
      text: `Top sellers to stock: ${topSellers}`,
      question: 'What are our top-selling items and how should I plan inventory?',
      severity: 'info',
    });
  }

  // COGS watch - high cost categories
  if (cogsSummary?.by_category) {
    const highCostCategory = [...cogsSummary.by_category]
      .sort((a, b) => b.cost - a.cost)[0];

    if (highCostCategory) {
      items.push({
        id: 'cogs-watch',
        text: `Highest cost category: ${highCostCategory.category} ($${highCostCategory.cost.toFixed(0)})`,
        question: "What's our COGS breakdown and are there any cost concerns?",
        severity: 'info',
      });
    }
  }

  // Gross margin status
  if (cogsSummary?.gross_margin) {
    const margin = cogsSummary.gross_margin;
    const targetMargin = 65; // Target 65%+ gross margin

    if (margin < targetMargin) {
      items.push({
        id: 'margin-watch',
        text: `Gross margin at ${margin.toFixed(1)}% - below target of ${targetMargin}%`,
        question: 'How can we improve our gross margin?',
        severity: 'warning',
      });
    } else {
      items.push({
        id: 'margin-good',
        text: `Gross margin at ${margin.toFixed(1)}% - on track`,
        question: 'Show me our margin breakdown',
        severity: 'info',
      });
    }
  }

  // Loyalty program insights
  if (loyaltyStats?.loyalty) {
    const loyaltyPct = loyaltyStats.loyalty.percentage;
    const targetLoyalty = 40; // Target 40%+ loyalty penetration

    if (loyaltyPct < targetLoyalty) {
      items.push({
        id: 'loyalty-low',
        text: `Loyalty at ${loyaltyPct.toFixed(0)}% - opportunity to grow (target: ${targetLoyalty}%)`,
        question: "How's our loyalty program performing and how can we improve it?",
        severity: 'info',
      });
    } else {
      items.push({
        id: 'loyalty-good',
        text: `Loyalty penetration at ${loyaltyPct.toFixed(0)}% - exceeding target`,
        question: "How's our loyalty program performance?",
        severity: 'info',
      });
    }
  }

  // Staffing recommendations based on best day
  if (weeklySummary?.sales) {
    items.push({
      id: 'staffing-rec',
      text: 'Review staffing levels for peak days',
      question: 'Based on our sales patterns, how should I plan staffing for next week?',
      severity: 'info',
    });
  }

  return (
    <InsightCard
      title="Planning Ahead"
      icon={<Target className="w-4 h-4" />}
      items={items}
      onAskAI={onAskAI}
      accentColor="green"
    />
  );
}
