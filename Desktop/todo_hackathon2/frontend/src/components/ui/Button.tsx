'use client';

import { ButtonProps } from '@/types/ui';
import { Loader2 } from 'lucide-react';

export default function Button({
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  children,
  onClick,
  type = 'button',
  className = '',
}: ButtonProps) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-100 active:bg-indigo-800',
    secondary: 'border-2 border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 hover:border-gray-400 focus:ring-gray-100 active:bg-gray-100',
    danger: 'bg-rose-600 text-white hover:bg-rose-700 focus:ring-rose-100 active:bg-rose-800',
  };

  const sizeStyles = {
    small: 'py-2 px-3 text-sm min-h-[40px]',
    medium: 'py-2.5 px-4 text-base min-h-[44px]',
    large: 'py-3 px-6 text-base md:text-lg min-h-[48px]',
  };

  const isDisabled = disabled || loading;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      aria-busy={loading}
      aria-disabled={isDisabled}
    >
      {loading && (
        <Loader2
          className="animate-spin mr-2"
          size={size === 'small' ? 14 : size === 'large' ? 20 : 16}
          aria-label="Loading"
        />
      )}
      {children}
    </button>
  );
}
