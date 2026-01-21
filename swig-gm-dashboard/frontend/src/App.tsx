import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Header from './components/common/Header';
import TabNavigation, { type TabId } from './components/common/TabNavigation';
import KPICards from './components/Dashboard/KPICards';
import ThroughputChart from './components/Dashboard/ThroughputChart';
import AlertBanner from './components/Dashboard/AlertBanner';
import WhoIsWorking from './components/Labor/WhoIsWorking';
import ComplianceCard from './components/Labor/ComplianceCard';
import ChatPanel from './components/Chat/ChatPanel';
import DailyRoster from './components/Labor/DailyRoster';
import SalesSummary from './components/Sales/SalesSummary';
import InventoryUsage from './components/Inventory/InventoryUsage';
import WeeklySummaryView from './components/Weekly/WeeklySummary';
import { getStores, getKPIs, getHourlyData, getAlerts, getWhosWorking, getViolations } from './services/api';

// Data range in the database
const MIN_DATE = '2025-01-06';
const MAX_DATE = '2025-01-26';

function App() {
  const [selectedStore, setSelectedStore] = useState(1001);
  const [selectedDate, setSelectedDate] = useState(MAX_DATE);
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  // Fetch stores
  const { data: stores = [] } = useQuery({
    queryKey: ['stores'],
    queryFn: getStores,
  });

  // Fetch KPIs
  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis', selectedStore, selectedDate],
    queryFn: () => getKPIs(selectedStore, selectedDate),
    enabled: selectedStore > 0,
  });

  // Fetch hourly data
  const { data: hourlyData, isLoading: hourlyLoading } = useQuery({
    queryKey: ['hourly', selectedStore, selectedDate],
    queryFn: () => getHourlyData(selectedStore, selectedDate),
    enabled: selectedStore > 0,
  });

  // Fetch alerts
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts', selectedStore, selectedDate],
    queryFn: () => getAlerts(selectedStore, selectedDate),
    enabled: selectedStore > 0,
  });

  // Fetch who's working
  const { data: employees, isLoading: employeesLoading } = useQuery({
    queryKey: ['whos-working', selectedStore, selectedDate],
    queryFn: () => getWhosWorking(selectedStore, selectedDate),
    enabled: selectedStore > 0,
  });

  // Fetch violations
  const { data: violations, isLoading: violationsLoading } = useQuery({
    queryKey: ['violations', selectedStore, selectedDate],
    queryFn: () => getViolations(selectedStore, 7, selectedDate),
    enabled: selectedStore > 0,
  });

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            {/* KPI Cards */}
            <section className="mb-6">
              <KPICards kpis={kpis} isLoading={kpisLoading} />
            </section>

            {/* Charts and Alerts Row */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2">
                <ThroughputChart
                  data={hourlyData}
                  isLoading={hourlyLoading}
                  storeId={selectedStore}
                  date={selectedDate}
                />
              </div>
              <div>
                <AlertBanner alerts={alerts} isLoading={alertsLoading} />
              </div>
            </section>

            {/* Labor and Chat Row */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="space-y-6">
                <WhoIsWorking employees={employees} isLoading={employeesLoading} />
              </div>
              <div>
                <ComplianceCard violations={violations} isLoading={violationsLoading} />
              </div>
              <div>
                <ChatPanel storeId={selectedStore} />
              </div>
            </section>
          </>
        );

      case 'workforce':
        return <DailyRoster storeId={selectedStore} date={selectedDate} />;

      case 'sales':
        return <SalesSummary storeId={selectedStore} date={selectedDate} />;

      case 'inventory':
        return <InventoryUsage storeId={selectedStore} date={selectedDate} />;

      case 'weekly':
        return <WeeklySummaryView storeId={selectedStore} date={selectedDate} />;

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header
        stores={stores}
        selectedStore={selectedStore}
        onStoreChange={setSelectedStore}
        selectedDate={selectedDate}
        onDateChange={setSelectedDate}
        minDate={MIN_DATE}
        maxDate={MAX_DATE}
      />

      {/* Tab Navigation */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {renderTabContent()}
      </main>
    </div>
  );
}

export default App;
