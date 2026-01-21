import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Trash2, Sparkles } from 'lucide-react';
import MessageBubble from './MessageBubble';
import SuggestedQueries from './SuggestedQueries';
import { sendChatMessage, clearSession } from '../../services/api';
import type { ChatMessage } from '../../types';
import type { TabId } from '../common/TabNavigation';
import { tabSuggestedQueries } from './tabSuggestedQueries';

interface ChatPanelProps {
  storeId: number;
  activeTab: TabId;
}

export default function ChatPanel({ storeId, activeTab }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQueries = tabSuggestedQueries[activeTab];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text.trim(), storeId, sessionId);
      setSessionId(response.session_id);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (sessionId) {
      try {
        await clearSession(sessionId);
      } catch (e) {
        console.error('Error clearing session:', e);
      }
    }
    setMessages([]);
    setSessionId(undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col h-[500px]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-swig-pink rounded-lg flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Assistant</h3>
            <p className="text-xs text-gray-500">Ask me anything about your store</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 chat-messages">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <MessageSquare className="w-12 h-12 text-gray-300 mb-3" />
            <p className="text-gray-500 mb-4">Ask me about your store's performance</p>
            {suggestedQueries && (
              <SuggestedQueries
                queries={suggestedQueries}
                onSelect={handleSend}
              />
            )}
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500 text-sm py-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-swig-pink rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-swig-pink rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-swig-pink rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about sales, compliance, employees..."
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-swig-pink focus:border-transparent text-sm"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || isLoading}
            className="p-2 bg-swig-pink text-white rounded-lg hover:bg-swig-pink-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
