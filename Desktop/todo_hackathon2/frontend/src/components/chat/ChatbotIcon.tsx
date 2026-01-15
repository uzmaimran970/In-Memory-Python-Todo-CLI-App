'use client';

import { useState } from 'react';
import { MessageCircle } from 'lucide-react';
import { ChatModal } from './ChatModal';

/**
 * Floating chat icon that opens the AI chatbot modal
 * Positioned fixed at bottom-right of screen
 */
export function ChatbotIcon() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button - Hidden when chat is open */}
      <button
        onClick={() => setIsOpen(true)}
        className={`
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-gradient-to-r from-purple-600 to-blue-600
          hover:from-purple-700 hover:to-blue-700
          text-white shadow-lg
          flex items-center justify-center
          transition-all duration-300
          hover:scale-110 hover:shadow-xl
          focus:outline-none focus:ring-4 focus:ring-purple-300
          ${isOpen ? 'hidden' : 'flex'}
        `}
        aria-label="Open chat assistant"
      >
        <MessageCircle className="w-6 h-6" />
      </button>

      {/* Chat Modal */}
      {isOpen && (
        <ChatModal onClose={() => setIsOpen(false)} />
      )}
    </>
  );
}
