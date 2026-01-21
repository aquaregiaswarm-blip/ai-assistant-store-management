import { useState } from 'react';
import InsightsPanel from './InsightsPanel';
import ChatPanel from '../Chat/ChatPanel';

interface SwigAIViewProps {
  storeId: number;
  date: string;
}

export default function SwigAIView({ storeId, date }: SwigAIViewProps) {
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  const handleAskAI = (question: string) => {
    // Set the pending message which will be picked up by the ChatPanel
    setPendingMessage(question);
  };

  return (
    <div className="h-[calc(100vh-180px)] flex flex-col lg:flex-row gap-6">
      {/* Left Panel - Insights */}
      <div className="lg:w-1/2 h-1/2 lg:h-full overflow-hidden">
        <InsightsPanel
          storeId={storeId}
          date={date}
          onAskAI={handleAskAI}
        />
      </div>

      {/* Right Panel - Chat */}
      <div className="lg:w-1/2 h-1/2 lg:h-full">
        <ChatPanel
          storeId={storeId}
          activeTab="swigai"
          variant="embedded"
          externalMessage={pendingMessage}
        />
      </div>
    </div>
  );
}
