'use client';

import { InputProps } from '@/types/ui';
import { useState, useEffect, useMemo } from 'react';

export default function Input({
  label,
  error,
  helperText,
  maxLength,
  showCharCount = false,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  required = false,
  className = '',
}: InputProps) {
  const [charCount, setCharCount] = useState(0);

  useEffect(() => {
    setCharCount(value.length);
  }, [value]);

  const hasError = !!error;
  const hasSuccess = !hasError && value.length > 0;

  // Minimum font size of 16px prevents iOS zoom on focus
  const baseInputStyles = 'w-full px-4 py-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 text-base min-h-[48px]';

  const stateStyles = hasError
    ? 'border-red-500 focus:ring-red-100 focus:border-red-500'
    : hasSuccess
    ? 'border-green-500 focus:ring-green-100 focus:border-green-500'
    : 'border-gray-300 focus:ring-indigo-100 focus:border-indigo-600';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (!maxLength || newValue.length <= maxLength) {
      onChange(newValue);
    }
  };

  // Use useMemo to keep inputId stable across renders - prevents focus loss
  const inputId = useMemo(
    () => `input-${label?.replace(/\s/g, '-').toLowerCase() || `id-${Math.random().toString(36).substr(2, 9)}`}`,
    [label]
  );

  const commonProps = {
    id: inputId,
    value,
    onChange: handleChange,
    placeholder,
    disabled,
    required,
    maxLength,
    className: `${baseInputStyles} ${stateStyles} ${className}`,
    'aria-invalid': hasError,
    'aria-describedby': error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined,
  };

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1.5"
        >
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      )}

      {type === 'textarea' ? (
        <textarea
          {...commonProps}
          rows={4}
          className={`${commonProps.className} resize-none`}
        />
      ) : (
        <input
          {...commonProps}
          type={type}
        />
      )}

      <div className="mt-1.5 flex items-center justify-between">
        <div className="flex-1">
          {error && (
            <p
              id={`${inputId}-error`}
              className="text-sm text-red-600"
              role="alert"
            >
              {error}
            </p>
          )}

          {!error && helperText && (
            <p
              id={`${inputId}-helper`}
              className="text-sm text-gray-500"
            >
              {helperText}
            </p>
          )}
        </div>

        {showCharCount && maxLength && (
          <span className="text-xs text-gray-500 ml-2">
            {charCount}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
}
