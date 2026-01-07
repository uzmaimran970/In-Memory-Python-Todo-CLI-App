import { Inbox } from 'lucide-react';
import Button from '@/components/ui/Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
  className?: string;
}

export default function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center ${className}`}
      role="status"
      aria-label={title}
    >
      {/* Icon */}
      <div className="mb-4 text-gray-300" aria-hidden="true">
        {icon || <Inbox size={64} strokeWidth={1.5} />}
      </div>

      {/* Title */}
      <h3 className="text-xl font-semibold text-gray-700 mb-2">
        {title}
      </h3>

      {/* Description */}
      <p className="text-gray-500 mb-6 max-w-md">
        {description}
      </p>

      {/* Optional Action Button */}
      {actionLabel && onAction && (
        <Button
          variant="primary"
          size="medium"
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

// Pre-configured variants for common use cases
export function EmptyTaskList({ onCreateTask }: { onCreateTask?: () => void }) {
  return (
    <EmptyState
      title="No tasks yet"
      description="Start by creating your first task. You can organize your work and track your progress easily."
      actionLabel={onCreateTask ? "Create Your First Task" : undefined}
      onAction={onCreateTask}
    />
  );
}

export function EmptySearchResults() {
  return (
    <EmptyState
      title="No results found"
      description="Try adjusting your search or filter criteria to find what you're looking for."
    />
  );
}

export function EmptyCompletedTasks() {
  return (
    <EmptyState
      title="No completed tasks"
      description="Tasks you mark as completed will appear here. Keep up the great work!"
    />
  );
}
