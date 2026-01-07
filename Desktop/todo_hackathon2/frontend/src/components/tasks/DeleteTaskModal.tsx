'use client';

import { useState, useEffect, useRef } from 'react';
import { Task } from '@/types';
import { api } from '@/lib/api';
import { toast } from 'react-hot-toast';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';

interface DeleteTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onTaskDeleted: (taskId: number) => void;
}

export default function DeleteTaskModal({
  isOpen,
  onClose,
  task,
  onTaskDeleted,
}: DeleteTaskModalProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

  // Focus cancel button when modal opens (safe default)
  useEffect(() => {
    if (isOpen && cancelButtonRef.current) {
      setTimeout(() => {
        cancelButtonRef.current?.focus();
      }, 150);
    }
  }, [isOpen]);

  // Handle null task gracefully
  if (!task) {
    return null;
  }

  const handleDelete = async () => {
    setIsDeleting(true);

    try {
      // Call API to delete task
      await api.deleteTask(task.id);

      // Optimistically remove task from UI
      onTaskDeleted(task.id);

      // Show success toast
      toast.success('Task deleted');

      // Close modal
      onClose();
    } catch (error) {
      // Show error toast
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
      toast.error(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancel = () => {
    if (!isDeleting) {
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleCancel} title="Delete Task">
      <div className="space-y-4">
        {/* Confirmation Message */}
        <div className="text-gray-700">
          <p className="mb-2">
            Are you sure you want to delete <strong className="font-semibold text-gray-900">"{task.title}"</strong>?
          </p>
          <p className="text-sm text-gray-600">
            This action cannot be undone.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          {/* Cancel Button - Auto-focused for safety */}
          <button
            ref={cancelButtonRef}
            onClick={handleCancel}
            disabled={isDeleting}
            className="px-4 py-2.5 text-base font-medium text-gray-700 bg-transparent border-2 border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-4 focus:ring-gray-100 active:bg-gray-100 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Cancel deletion"
          >
            Cancel
          </button>

          {/* Delete Button - Danger variant */}
          <Button
            variant="danger"
            onClick={handleDelete}
            loading={isDeleting}
            disabled={isDeleting}
            aria-label="Confirm deletion"
            aria-busy={isDeleting}
          >
            Delete Task
          </Button>
        </div>
      </div>
    </Modal>
  );
}
