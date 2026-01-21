import { useState } from 'react';
import { Sparkles, X } from 'lucide-react';
import ChatPanel from './ChatPanel';
import type { TabId } from '../common/TabNavigation';

interface GlobalChatWidgetProps {
  storeId: number;
  activeTab: TabId;
  hidden?: boolean;
}

export default function GlobalChatWidget({ storeId, activeTab, hidden = false }: GlobalChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Don't render anything when hidden (e.g., on SwigAI tab where chat is embedded)
  if (hidden) {
    return null;
  }

  return (
    <>
      {/* Floating Action Button - always visible when closed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 z-50 flex items-center gap-2 px-4 py-3 bg-swig-pink text-white rounded-full shadow-lg hover:bg-swig-pink-dark hover:shadow-xl transition-all duration-200 transform hover:scale-105"
          aria-label="Open SwigAI Assistant"
        >
          <Sparkles className="w-5 h-5" />
          <span className="font-medium">SwigAI</span>
        </button>
      )}

      {/* Chat Panel Container - slides up when open */}
      <div
        className={`fixed bottom-4 right-4 z-50 w-[380px] transition-all duration-300 ease-out ${
          isOpen
            ? 'opacity-100 translate-y-0 pointer-events-auto'
            : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
        style={{ maxHeight: 'calc(100vh - 2rem)' }}
      >
        <div className="relative">
          {/* Close button overlay */}
          <button
            onClick={() => setIsOpen(false)}
            className="absolute -top-2 -right-2 z-10 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
            aria-label="Close chat"
          >
            <X className="w-4 h-4" />
          </button>

          <ChatPanel storeId={storeId} activeTab={activeTab} />
        </div>
      </div>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40 sm:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
