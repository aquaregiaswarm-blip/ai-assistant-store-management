import type { Store } from '../../types';

interface StoreSelectorProps {
  stores: Store[];
  selectedStore: number;
  onChange: (storeId: number) => void;
}

export default function StoreSelector({ stores, selectedStore, onChange }: StoreSelectorProps) {
  return (
    <select
      value={selectedStore}
      onChange={(e) => onChange(Number(e.target.value))}
      className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-swig-pink focus:border-transparent cursor-pointer"
    >
      {stores.map((store) => (
        <option key={store.store_id} value={store.store_id}>
          {store.store_name} (#{store.store_id})
        </option>
      ))}
    </select>
  );
}
