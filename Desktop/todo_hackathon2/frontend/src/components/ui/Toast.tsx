'use client';

import { Toaster, toast as hotToast } from 'react-hot-toast';
import { CheckCircle2, XCircle, Info } from 'lucide-react';

// Toast configuration
export const toastConfig = {
  duration: 5000,
  position: 'bottom-right' as const,
  style: {
    borderRadius: '8px',
    fontSize: '14px',
    padding: '12px 16px',
    maxWidth: '400px',
  },
};

// Custom toast variants
export const toast = {
  success: (message: string) => {
    hotToast.custom(
      (t) => (
        <div
          className={`
            flex items-center gap-3 bg-green-50 text-green-800 border border-green-200
            rounded-lg px-4 py-3 shadow-lg transition-all duration-300
            ${t.visible ? 'animate-enter' : 'animate-leave'}
          `}
          role="alert"
          aria-live="polite"
        >
          <CheckCircle2 size={20} className="flex-shrink-0 text-green-600" aria-hidden="true" />
          <p className="flex-1 font-medium">{message}</p>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="flex-shrink-0 text-green-600 hover:text-green-800 transition-colors"
            aria-label="Dismiss notification"
          >
            <XCircle size={18} />
          </button>
        </div>
      ),
      { duration: toastConfig.duration }
    );
  },

  error: (message: string) => {
    hotToast.custom(
      (t) => (
        <div
          className={`
            flex items-center gap-3 bg-red-50 text-red-800 border border-red-200
            rounded-lg px-4 py-3 shadow-lg transition-all duration-300
            ${t.visible ? 'animate-enter' : 'animate-leave'}
          `}
          role="alert"
          aria-live="assertive"
        >
          <XCircle size={20} className="flex-shrink-0 text-red-600" aria-hidden="true" />
          <p className="flex-1 font-medium">{message}</p>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="flex-shrink-0 text-red-600 hover:text-red-800 transition-colors"
            aria-label="Dismiss notification"
          >
            <XCircle size={18} />
          </button>
        </div>
      ),
      { duration: toastConfig.duration }
    );
  },

  info: (message: string) => {
    hotToast.custom(
      (t) => (
        <div
          className={`
            flex items-center gap-3 bg-blue-50 text-blue-800 border border-blue-200
            rounded-lg px-4 py-3 shadow-lg transition-all duration-300
            ${t.visible ? 'animate-enter' : 'animate-leave'}
          `}
          role="status"
          aria-live="polite"
        >
          <Info size={20} className="flex-shrink-0 text-blue-600" aria-hidden="true" />
          <p className="flex-1 font-medium">{message}</p>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="flex-shrink-0 text-blue-600 hover:text-blue-800 transition-colors"
            aria-label="Dismiss notification"
          >
            <XCircle size={18} />
          </button>
        </div>
      ),
      { duration: toastConfig.duration }
    );
  },
};

// Toaster component to be added to layout
export function ToastProvider() {
  return (
    <Toaster
      position={toastConfig.position}
      toastOptions={{
        duration: toastConfig.duration,
        style: toastConfig.style,
      }}
    />
  );
}

// Export for convenience
export { Toaster };
