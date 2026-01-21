import { Store, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import StoreSelector from './StoreSelector';
import type { Store as StoreType } from '../../types';

interface HeaderProps {
  stores: StoreType[];
  selectedStore: number;
  onStoreChange: (storeId: number) => void;
  selectedDate: string;
  onDateChange: (date: string) => void;
  minDate: string;
  maxDate: string;
}

export default function Header({
  stores,
  selectedStore,
  onStoreChange,
  selectedDate,
  onDateChange,
  minDate,
  maxDate
}: HeaderProps) {
  const selectedStoreData = stores.find(s => s.store_id === selectedStore);

  // Format date for display
  const formatDisplayDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Navigate to previous/next day
  const changeDay = (delta: number) => {
    const current = new Date(selectedDate + 'T00:00:00');
    current.setDate(current.getDate() + delta);
    const newDate = current.toISOString().split('T')[0];

    if (newDate >= minDate && newDate <= maxDate) {
      onDateChange(newDate);
    }
  };

  const canGoPrev = selectedDate > minDate;
  const canGoNext = selectedDate < maxDate;

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Swig Logo placeholder */}
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-swig-pink rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">GM Dashboard</h1>
              <p className="text-sm text-gray-500">AI-Powered Insights</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {/* Store Selector */}
          <div className="flex items-center gap-2">
            <Store className="w-5 h-5 text-gray-500" />
            <StoreSelector
              stores={stores}
              selectedStore={selectedStore}
              onChange={onStoreChange}
            />
          </div>

          {/* Date Picker */}
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div className="flex items-center gap-1">
              <button
                onClick={() => changeDay(-1)}
                disabled={!canGoPrev}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
                title="Previous day"
              >
                <ChevronLeft className="w-4 h-4 text-gray-600" />
              </button>

              <input
                type="date"
                value={selectedDate}
                onChange={(e) => onDateChange(e.target.value)}
                min={minDate}
                max={maxDate}
                className="px-2 py-1 border border-gray-300 rounded text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-swig-pink focus:border-transparent"
              />

              <button
                onClick={() => changeDay(1)}
                disabled={!canGoNext}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
                title="Next day"
              >
                <ChevronRight className="w-4 h-4 text-gray-600" />
              </button>
            </div>
            <span className="text-sm text-gray-500 hidden lg:inline">
              {formatDisplayDate(selectedDate)}
            </span>
          </div>

          {/* Selected Store Info */}
          {selectedStoreData && (
            <div className="text-sm text-gray-600 hidden md:block">
              {selectedStoreData.city}, {selectedStoreData.state}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
