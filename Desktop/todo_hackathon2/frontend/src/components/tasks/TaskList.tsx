'use client';

import { memo } from 'react';
import { Task, FilterType } from '@/types';
import TaskCard from './TaskCard';
import { EmptyTaskList, EmptyCompletedTasks } from '@/components/layout/EmptyState';
import { ListFilter } from 'lucide-react';

interface TaskListProps {
  tasks: Task[];
  filter: FilterType;
  onTaskUpdate: (updatedTask: Task) => void;
  onTaskEdit: (task: Task) => void;
  onTaskDelete: (task: Task) => void;
  highlightedTaskId?: number | null;
  highlightType?: 'create' | 'update' | null;
}

function TaskList({
  tasks,
  filter,
  onTaskUpdate,
  onTaskEdit,
  onTaskDelete,
  highlightedTaskId,
  highlightType
}: TaskListProps) {
  // Filter tasks based on active filter
  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') return !task.is_completed;
    if (filter === 'completed') return task.is_completed;
    return true; // 'all'
  });

  // Sort by created_at descending (newest first)
  const sortedTasks = [...filteredTasks].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  // Handle empty states
  if (sortedTasks.length === 0) {
    if (filter === 'completed') {
      return <EmptyCompletedTasks />;
    }

    if (filter === 'active' && tasks.some(t => t.is_completed)) {
      return (
        <div className="flex flex-col items-center justify-center p-12 text-center">
          <div className="mb-4 text-gray-300" aria-hidden="true">
            <ListFilter size={64} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            No active tasks
          </h3>
          <p className="text-gray-500 max-w-md">
            All your tasks are completed! Great job! Create a new task to get started.
          </p>
        </div>
      );
    }

    return <EmptyTaskList />;
  }

  return (
    <div
      className="space-y-3"
      role="list"
      aria-label={`${filter} tasks list`}
    >
      {sortedTasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggle={onTaskUpdate}
          onEdit={() => onTaskEdit(task)}
          onDelete={() => onTaskDelete(task)}
          isHighlighted={highlightedTaskId === task.id}
          highlightType={highlightedTaskId === task.id ? highlightType : null}
        />
      ))}
    </div>
  );
}

export default memo(TaskList);
