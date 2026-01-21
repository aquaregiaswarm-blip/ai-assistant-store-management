import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export interface InsightItem {
  id: string;
  text: string;
  question: string;
  severity?: 'info' | 'warning' | 'critical';
}

interface InsightCardProps {
  title: string;
  icon: React.ReactNode;
  items: InsightItem[];
  onAskAI: (question: string) => void;
  defaultExpanded?: boolean;
  accentColor?: 'red' | 'orange' | 'blue' | 'green';
}

const accentStyles = {
  red: 'bg-red-50 border-red-200',
  orange: 'bg-orange-50 border-orange-200',
  blue: 'bg-blue-50 border-blue-200',
  green: 'bg-green-50 border-green-200',
};

const iconBgStyles = {
  red: 'bg-red-100 text-red-600',
  orange: 'bg-orange-100 text-orange-600',
  blue: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
};

const severityStyles = {
  info: 'text-gray-700 hover:bg-gray-100',
  warning: 'text-orange-700 hover:bg-orange-100',
  critical: 'text-red-700 hover:bg-red-100',
};

export default function InsightCard({
  title,
  icon,
  items,
  onAskAI,
  defaultExpanded = true,
  accentColor = 'blue',
}: InsightCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`rounded-xl border ${accentStyles[accentColor]} overflow-hidden`}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-white/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconBgStyles[accentColor]}`}>
            {icon}
          </div>
          <span className="font-semibold text-gray-900">{title}</span>
          {items.length > 0 && (
            <span className="text-xs bg-white/80 px-2 py-0.5 rounded-full text-gray-600">
              {items.length} {items.length === 1 ? 'item' : 'items'}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        )}
      </button>

      {/* Items */}
      {isExpanded && (
        <div className="px-4 pb-4">
          {items.length === 0 ? (
            <p className="text-sm text-gray-500 italic py-2">No items to show</p>
          ) : (
            <ul className="space-y-1">
              {items.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => onAskAI(item.question)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${severityStyles[item.severity || 'info']}`}
                  >
                    {item.text}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
