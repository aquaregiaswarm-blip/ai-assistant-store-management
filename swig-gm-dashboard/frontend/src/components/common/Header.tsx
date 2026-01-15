import { Store } from 'lucide-react';
import StoreSelector from './StoreSelector';
import type { Store as StoreType } from '../../types';

interface HeaderProps {
  stores: StoreType[];
  selectedStore: number;
  onStoreChange: (storeId: number) => void;
  currentDate: string;
}

export default function Header({ stores, selectedStore, onStoreChange, currentDate }: HeaderProps) {
  const selectedStoreData = stores.find(s => s.store_id === selectedStore);

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

          {/* Current Date */}
          <div className="text-sm">
            <span className="text-gray-500">Data Date: </span>
            <span className="font-medium text-gray-900">{currentDate}</span>
          </div>

          {/* Selected Store Info */}
          {selectedStoreData && (
            <div className="text-sm text-gray-600">
              {selectedStoreData.city}, {selectedStoreData.state}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
