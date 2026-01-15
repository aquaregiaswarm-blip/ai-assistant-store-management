import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Header from './components/common/Header';
import KPICards from './components/Dashboard/KPICards';
import ThroughputChart from './components/Dashboard/ThroughputChart';
import AlertBanner from './components/Dashboard/AlertBanner';
import WhoIsWorking from './components/Labor/WhoIsWorking';
import ComplianceCard from './components/Labor/ComplianceCard';
import ChatPanel from './components/Chat/ChatPanel';
import { getStores, getKPIs, getHourlyData, getAlerts, getWhosWorking, getViolations } from './services/api';

const DATA_DATE = '2025-01-26'; // Current date in the database

function App() {
  const [selectedStore, setSelectedStore] = useState(1001);

  // Fetch stores
  const { data: stores = [] } = useQuery({
    queryKey: ['stores'],
    queryFn: getStores,
  });

  // Fetch KPIs
  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ['kpis', selectedStore],
    queryFn: () => getKPIs(selectedStore),
    enabled: selectedStore > 0,
  });

  // Fetch hourly data
  const { data: hourlyData, isLoading: hourlyLoading } = useQuery({
    queryKey: ['hourly', selectedStore],
    queryFn: () => getHourlyData(selectedStore),
    enabled: selectedStore > 0,
  });

  // Fetch alerts
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts', selectedStore],
    queryFn: () => getAlerts(selectedStore),
    enabled: selectedStore > 0,
  });

  // Fetch who's working
  const { data: employees, isLoading: employeesLoading } = useQuery({
    queryKey: ['whos-working', selectedStore],
    queryFn: () => getWhosWorking(selectedStore),
    enabled: selectedStore > 0,
  });

  // Fetch violations
  const { data: violations, isLoading: violationsLoading } = useQuery({
    queryKey: ['violations', selectedStore],
    queryFn: () => getViolations(selectedStore, 7),
    enabled: selectedStore > 0,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header
        stores={stores}
        selectedStore={selectedStore}
        onStoreChange={setSelectedStore}
        currentDate={DATA_DATE}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* KPI Cards */}
        <section className="mb-6">
          <KPICards kpis={kpis} isLoading={kpisLoading} />
        </section>

        {/* Charts and Alerts Row */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <ThroughputChart data={hourlyData} isLoading={hourlyLoading} />
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
      </main>
    </div>
  );
}

export default App;
