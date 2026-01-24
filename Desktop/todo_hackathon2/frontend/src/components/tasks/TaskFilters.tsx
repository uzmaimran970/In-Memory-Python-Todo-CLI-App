'use client';

import { FilterType } from '@/types';
import { Search, SortAsc, Filter } from 'lucide-react';
import { useState } from 'react';

interface TaskFiltersProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  sortBy?: string;
  onSortChange?: (sort: string) => void;
  priorityFilter?: string;
  onPriorityChange?: (priority: string) => void;
}

export default function TaskFilters({
  activeFilter,
  onFilterChange,
  searchQuery = '',
  onSearchChange,
  sortBy = 'created',
  onSortChange,
  priorityFilter = 'all',
  onPriorityChange,
}: TaskFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const filters: { label: string; value: FilterType }[] = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
  ];

  const sortOptions = [
    { label: 'Newest', value: 'created' },
    { label: 'Title', value: 'title' },
    { label: 'Priority', value: 'priority' },
    { label: 'Due Date', value: 'due_date' },
  ];

  const priorityOptions = [
    { label: 'All Priorities', value: 'all' },
    { label: 'High', value: 'high' },
    { label: 'Medium', value: 'medium' },
    { label: 'Low', value: 'low' },
  ];

  return (
    <div className="space-y-3 mb-5 md:mb-6">
      {/* Status Filters Row */}
      <div className="flex flex-wrap items-center gap-2 md:gap-3" role="group" aria-label="Task filters">
        {filters.map((filter) => {
          const isActive = activeFilter === filter.value;
          return (
            <button
              key={filter.value}
              onClick={() => onFilterChange(filter.value)}
              className={`
                flex-1 sm:flex-none px-4 py-2.5 rounded-lg border transition-all duration-200 text-sm md:text-base min-h-[44px]
                focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
                ${isActive
                  ? 'bg-indigo-100 text-indigo-700 font-semibold border-indigo-200'
                  : 'text-gray-600 hover:bg-gray-100 border-gray-200'
                }
              `}
              aria-pressed={isActive}
            >
              {filter.label}
            </button>
          );
        })}

        {/* Advanced Filter Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`ml-auto px-3 py-2.5 rounded-lg border transition-all text-sm min-h-[44px] flex items-center gap-1.5 ${
            showAdvanced ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'border-gray-200 text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Filter size={16} />
          <span className="hidden sm:inline">Filters</span>
        </button>
      </div>

      {/* Search + Sort + Priority Row */}
      {showAdvanced && (
        <div className="flex flex-wrap items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200 animate-in slide-in-from-top-1">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => onSearchChange?.(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Priority Filter */}
          <div className="relative">
            <select
              value={priorityFilter}
              onChange={(e) => onPriorityChange?.(e.target.value)}
              className="appearance-none pl-3 pr-8 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 focus:outline-none cursor-pointer"
            >
              {priorityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="relative flex items-center gap-1.5">
            <SortAsc size={14} className="text-gray-400" />
            <select
              value={sortBy}
              onChange={(e) => onSortChange?.(e.target.value)}
              className="appearance-none pl-3 pr-8 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 focus:outline-none cursor-pointer"
            >
              {sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
}
