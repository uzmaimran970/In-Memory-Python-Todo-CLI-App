'use client';

import { ModalProps } from '@/types/ui';
import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  className = '',
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Handle escape key press
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Save current focus and prevent body scroll
      previousActiveElement.current = document.activeElement as HTMLElement;
      document.body.style.overflow = 'hidden';
    } else {
      // Restore focus when modal closes
      document.body.style.overflow = 'unset';
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // Click outside to close
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end md:items-center justify-center overflow-y-auto md:overflow-hidden"
      onClick={handleBackdropClick}
      aria-labelledby="modal-title"
      aria-modal="true"
      role="dialog"
    >
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300" aria-hidden="true" />

      {/* Modal Content - Bottom sheet on mobile, centered on desktop */}
      <div
        ref={modalRef}
        tabIndex={-1}
        className={`
          relative z-50 bg-white shadow-xl
          w-full md:max-w-lg md:mx-4
          transition-all duration-300
          ${isOpen
            ? 'translate-y-0 md:scale-100 opacity-100'
            : 'translate-y-full md:translate-y-0 md:scale-95 opacity-0'
          }
          rounded-t-2xl md:rounded-lg
          max-h-[90vh] md:max-h-[85vh] overflow-hidden
          flex flex-col
          pb-safe
          ${className}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 md:px-6 py-4 border-b border-gray-200 flex-shrink-0">
          {/* Mobile drag indicator */}
          <div className="md:hidden absolute top-2 left-1/2 -translate-x-1/2">
            <div className="w-10 h-1 bg-gray-300 rounded-full" aria-hidden="true" />
          </div>

          <h2
            id="modal-title"
            className="text-lg md:text-xl font-semibold text-gray-900 mt-2 md:mt-0"
          >
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-1 md:p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600 min-w-[44px] min-h-[44px] flex items-center justify-center -mr-2"
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body - Scrollable */}
        <div className="px-4 md:px-6 py-4 overflow-y-auto flex-1">
          {children}
        </div>
      </div>
    </div>
  );
}
