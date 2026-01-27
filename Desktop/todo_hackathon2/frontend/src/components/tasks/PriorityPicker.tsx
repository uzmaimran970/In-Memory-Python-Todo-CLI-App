'use client';

import { memo } from 'react';
import { TaskPriority } from '@/types';

interface PriorityPickerProps {
  value: TaskPriority;
  onChange: (priority: TaskPriority) => void;
  disabled?: boolean;
}

const priorities: { value: TaskPriority; label: string; color: string; icon: string }[] = [
  { value: 'high', label: 'High', color: 'text-red-600 bg-red-50 border-red-200 hover:bg-red-100', icon: '🔴' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600 bg-yellow-50 border-yellow-200 hover:bg-yellow-100', icon: '🟡' },
  { value: 'low', label: 'Low', color: 'text-green-600 bg-green-50 border-green-200 hover:bg-green-100', icon: '🟢' },
];

function PriorityPicker({ value, onChange, disabled = false }: PriorityPickerProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        Priority
      </label>
      <div className="flex gap-2">
        {priorities.map((priority) => (
          <button
            key={priority.value}
            type="button"
            onClick={() => onChange(priority.value)}
            disabled={disabled}
            className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-200 ${
              value === priority.value
                ? `${priority.color} ring-2 ring-offset-1 ring-current`
                : 'text-gray-500 bg-gray-50 border-gray-200 hover:bg-gray-100'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <span className="mr-1">{priority.icon}</span>
            {priority.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default memo(PriorityPicker);
