export type TabId = 'overview' | 'workforce' | 'sales' | 'inventory' | 'weekly';

interface Tab {
  id: TabId;
  label: string;
}

const tabs: Tab[] = [
  { id: 'overview', label: 'Daily Overview' },
  { id: 'workforce', label: 'Workforce' },
  { id: 'sales', label: 'Sales' },
  { id: 'inventory', label: 'Inventory' },
  { id: 'weekly', label: 'Weekly' },
];

interface TabNavigationProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export default function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="bg-white border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-6">
        <nav className="flex space-x-1" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                px-5 py-3.5 text-sm font-semibold border-b-3 transition-all duration-200
                ${activeTab === tab.id
                  ? 'border-swig-red text-swig-red'
                  : 'border-transparent text-swig-slate hover:text-swig-navy hover:border-swig-slate-light'
                }
              `}
              style={{ borderBottomWidth: '3px' }}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}
