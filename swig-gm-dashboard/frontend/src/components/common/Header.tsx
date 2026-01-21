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
    <header className="bg-white shadow-card px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Swig Logo */}
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-swig-red rounded-full flex items-center justify-center shadow-md">
              <span className="text-white font-display font-bold text-xl">S</span>
            </div>
            <div>
              <h1 className="text-xl font-display font-bold text-swig-navy">GM Dashboard</h1>
              <p className="text-sm text-swig-slate">AI-Powered Insights</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          {/* Store Selector */}
          <div className="flex items-center gap-2">
            <Store className="w-5 h-5 text-swig-slate" />
            <StoreSelector
              stores={stores}
              selectedStore={selectedStore}
              onChange={onStoreChange}
            />
          </div>

          {/* Date Picker */}
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-swig-slate" />
            <div className="flex items-center gap-1">
              <button
                onClick={() => changeDay(-1)}
                disabled={!canGoPrev}
                className="p-1.5 rounded-full hover:bg-swig-card disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="Previous day"
              >
                <ChevronLeft className="w-4 h-4 text-swig-navy" />
              </button>

              <input
                type="date"
                value={selectedDate}
                onChange={(e) => onDateChange(e.target.value)}
                min={minDate}
                max={maxDate}
                className="px-3 py-1.5 border border-swig-slate-light rounded-lg text-sm font-medium text-swig-navy
                           focus:outline-none focus:ring-2 focus:ring-swig-red focus:border-transparent
                           bg-white hover:border-swig-slate transition-colors"
              />

              <button
                onClick={() => changeDay(1)}
                disabled={!canGoNext}
                className="p-1.5 rounded-full hover:bg-swig-card disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="Next day"
              >
                <ChevronRight className="w-4 h-4 text-swig-navy" />
              </button>
            </div>
            <span className="text-sm text-swig-slate hidden lg:inline">
              {formatDisplayDate(selectedDate)}
            </span>
          </div>

          {/* Selected Store Info */}
          {selectedStoreData && (
            <div className="text-sm font-medium text-swig-navy hidden md:block">
              {selectedStoreData.city}, {selectedStoreData.state}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
