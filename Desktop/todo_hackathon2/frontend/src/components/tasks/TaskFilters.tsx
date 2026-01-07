'use client';

import { FilterType } from '@/types';

interface TaskFiltersProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
}

export default function TaskFilters({ activeFilter, onFilterChange }: TaskFiltersProps) {
  const filters: { label: string; value: FilterType }[] = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 md:gap-3 mb-5 md:mb-6" role="group" aria-label="Task filters">
      {filters.map((filter) => {
        const isActive = activeFilter === filter.value;

        return (
          <button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            className={`
              flex-1 sm:flex-none px-4 py-2.5 rounded-lg border transition-all duration-200 text-sm md:text-base min-h-[44px]
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
              ${
                isActive
                  ? 'bg-indigo-100 text-indigo-700 font-semibold border-indigo-200'
                  : 'text-gray-600 hover:bg-gray-100 border-gray-200'
              }
            `}
            aria-pressed={isActive}
            aria-label={`Show ${filter.label.toLowerCase()} tasks`}
          >
            {filter.label}
          </button>
        );
      })}
    </div>
  );
}
