import type { TabId } from '../common/TabNavigation';
import type { SuggestedQuery } from '../../types';

export const tabSuggestedQueries: Record<TabId, SuggestedQuery[]> = {
  swigai: [
    { text: 'What should I focus on for the rest of today?', category: 'planning' },
    { text: 'Help me plan staffing for tomorrow', category: 'staffing' },
    { text: 'What are the trends I should know about?', category: 'trends' },
    { text: 'Are there any compliance risks this week?', category: 'compliance' },
    { text: 'What inventory should I be watching?', category: 'inventory' },
    { text: 'Give me a briefing for the week ahead', category: 'planning' },
  ],
  overview: [
    { text: 'How did we do yesterday?', category: 'performance' },
    { text: 'What was our peak hour?', category: 'operations' },
    { text: 'Any compliance issues I should know about?', category: 'compliance' },
    { text: "Who's working today?", category: 'workforce' },
    { text: "Who's my best linebuster?", category: 'workforce' },
    { text: 'What are our top-selling items?', category: 'sales' },
  ],
  workforce: [
    { text: 'Who is scheduled today?', category: 'schedule' },
    { text: 'Any employees approaching overtime?', category: 'labor' },
    { text: 'Are there any late arrivals today?', category: 'attendance' },
    { text: 'Which minors are working and when do they need breaks?', category: 'compliance' },
    { text: 'Show me break violations this week', category: 'compliance' },
    { text: 'Who has the most hours this week?', category: 'labor' },
  ],
  sales: [
    { text: 'What are our top-selling items today?', category: 'products' },
    { text: 'How is revenue by category?', category: 'revenue' },
    { text: "What's our average ticket size?", category: 'metrics' },
    { text: 'Compare sales to last week', category: 'trends' },
    { text: 'What payment methods are customers using?', category: 'payments' },
    { text: "How's loyalty program performance?", category: 'loyalty' },
  ],
  inventory: [
    { text: 'What ingredients are we using the most?', category: 'usage' },
    { text: "What's our COGS percentage today?", category: 'costs' },
    { text: 'Which category has highest ingredient cost?', category: 'costs' },
    { text: 'Show me gross margin breakdown', category: 'margins' },
    { text: "What's the cost breakdown by ingredient category?", category: 'costs' },
    { text: 'Are we on track with food cost?', category: 'targets' },
  ],
  weekly: [
    { text: 'How did this week compare to last week?', category: 'comparison' },
    { text: "What's our best day of the week?", category: 'trends' },
    { text: 'Show me weekly revenue trend', category: 'trends' },
    { text: "How's labor cost trending this week?", category: 'labor' },
    { text: 'What are our weekly top sellers?', category: 'products' },
    { text: 'Are we hitting labor percentage targets?', category: 'targets' },
  ],
};
