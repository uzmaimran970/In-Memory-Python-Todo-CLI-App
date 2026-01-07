'use client';

import { useState, memo, useEffect } from 'react';
import { Task } from '@/types';
import { CheckCircle2, Circle, Pencil, Trash2, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'react-hot-toast';

interface TaskCardProps {
  task: Task;
  onToggle: (updatedTask: Task) => void;
  onEdit: () => void;
  onDelete: () => void;
  isHighlighted?: boolean;
  highlightType?: 'create' | 'update' | null;
  onDeleting?: () => void;
}

function TaskCard({ task, onToggle, onEdit, onDelete, isHighlighted = false, highlightType = null, onDeleting }: TaskCardProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  // Initialize with boolean to avoid controlled/uncontrolled warning
  const [localCompleted, setLocalCompleted] = useState(Boolean(task.is_completed));

  // Sync local state when task prop changes
  useEffect(() => {
    setLocalCompleted(Boolean(task.is_completed));
  }, [task.is_completed]);

  const handleToggle = async () => {
    const newCompleted = !localCompleted;

    // Update local state immediately (optimistic update)
    setLocalCompleted(newCompleted);
    setIsToggling(true);

    try {
      // Call API to toggle task completion
      const updatedTask = await api.toggleTask(task.id);

      // Call parent callback to update task list with new data
      onToggle(updatedTask);

      // Show success toast
      toast.success(
        updatedTask.is_completed
          ? 'Task completed! ✓'
          : 'Task marked as active!'
      );
    } catch (error) {
      // Revert on error
      setLocalCompleted(!newCompleted);

      // Show error toast
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      toast.error(errorMessage);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = () => {
    // Trigger fade-out animation
    setIsFadingOut(true);

    // After animation completes, call onDelete
    setTimeout(() => {
      onDelete();
    }, 300);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const truncateDescription = (description: string | undefined): string => {
    if (!description) return '';
    return description.length > 100 ? `${description.substring(0, 100)}...` : description;
  };

  // Determine highlight styling based on type
  const getHighlightStyles = () => {
    if (!isHighlighted) {
      return 'border-gray-200 hover:bg-gray-50';
    }

    if (highlightType === 'update') {
      return 'border-indigo-500 bg-indigo-50 animate-pulse';
    }

    // Default to emerald for 'create' or null
    return 'border-emerald-500 bg-emerald-50 animate-pulse';
  };

  return (
    <div
      className={`
        group rounded-lg p-4 md:p-5 border transition-all duration-300 hover:shadow-md
        ${getHighlightStyles()}
        ${isFadingOut ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}
      `}
      role="article"
      aria-label={`Task: ${task.title}`}
    >
      <div className="flex items-start gap-3">
        {/* Completion Checkbox */}
        <div className="flex-shrink-0 flex items-center justify-center min-w-[44px] min-h-[44px] -m-2">
          <input
            type="checkbox"
            checked={localCompleted}
            onChange={handleToggle}
            disabled={isToggling}
            className="w-5 h-5 rounded cursor-pointer accent-indigo-600 focus:ring-indigo-500 disabled:opacity-50"
          />
        </div>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3
            className={`
              text-base font-semibold text-gray-900 mb-1 transition-all duration-300
              ${localCompleted ? 'line-through text-gray-500 opacity-60' : ''}
            `}
          >
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p
              className={`
                text-sm md:text-base text-gray-600 mb-2 transition-all duration-300
                ${localCompleted ? 'line-through text-gray-400 opacity-60' : ''}
              `}
            >
              {truncateDescription(task.description)}
            </p>
          )}

          {/* Created Date */}
          <p className="text-xs md:text-sm text-gray-400">
            Created {formatDate(task.created_at)}
          </p>
        </div>

        {/* Action Buttons - Always visible on mobile, hover on desktop */}
        <div className="flex items-center gap-1 md:gap-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={onEdit}
            className="flex items-center justify-center min-w-[44px] min-h-[44px] p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            aria-label="Edit task"
          >
            <Pencil size={18} />
          </button>

          <button
            onClick={handleDelete}
            className="flex items-center justify-center min-w-[44px] min-h-[44px] p-2 rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
            aria-label="Delete task"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default memo(TaskCard);
