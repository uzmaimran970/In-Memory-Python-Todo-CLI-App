'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import { Task, UpdateTaskData } from '@/types';
import { api } from '@/lib/api';
import { validateTitle, validateDescription } from '@/lib/validation';
import { toast } from 'react-hot-toast';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface EditTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onTaskUpdated: (task: Task) => void;
}

function EditTaskModal({
  isOpen,
  onClose,
  task,
  onTaskUpdated,
}: EditTaskModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [titleError, setTitleError] = useState<string | null>(null);
  const [descriptionError, setDescriptionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Store original values to detect changes
  const [originalTitle, setOriginalTitle] = useState('');
  const [originalDescription, setOriginalDescription] = useState('');

  // Initialize form with task data when modal opens or task changes
  useEffect(() => {
    if (task && isOpen) {
      setTitle(task.title);
      setDescription(task.description || '');
      setOriginalTitle(task.title);
      setOriginalDescription(task.description || '');
      // Clear any previous errors
      setTitleError(null);
      setDescriptionError(null);
    }
  }, [task, isOpen]);

  // Check if form has unsaved changes
  const hasUnsavedChanges =
    title.trim() !== originalTitle.trim() ||
    description.trim() !== originalDescription.trim();

  // Reset form state to original task data
  const resetForm = () => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
    }
    setTitleError(null);
    setDescriptionError(null);
    setIsSubmitting(false);
  };

  // Handle modal close with unsaved changes warning
  const handleClose = () => {
    if (hasUnsavedChanges && !isSubmitting) {
      const confirmDiscard = window.confirm(
        'You have unsaved changes. Are you sure you want to discard them?'
      );
      if (!confirmDiscard) {
        return;
      }
    }
    resetForm();
    onClose();
  };

  // Validate form before submission
  const validateForm = (): boolean => {
    const titleValidation = validateTitle(title);
    const descriptionValidation = validateDescription(description);

    setTitleError(titleValidation);
    setDescriptionError(descriptionValidation);

    return !titleValidation && !descriptionValidation;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!task) return;

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const taskData: UpdateTaskData = {
        title: title.trim(),
        description: description.trim() || undefined,
      };

      const updatedTask = await api.updateTask(task.id, taskData);

      // Show success toast
      toast.success('Task updated');

      // Call parent callback to update task in list
      onTaskUpdated(updatedTask);

      // Reset form and close modal
      resetForm();
      onClose();
    } catch (error) {
      // Keep modal open and preserve user input on error
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle title change with real-time validation - useCallback prevents re-renders
  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTitle(value);
    // Clear error when user starts typing
    setTitleError(null);
  }, []);

  // Handle description change with real-time validation - useCallback prevents re-renders
  const handleDescriptionChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setDescription(value);
    // Clear error when user starts typing
    setDescriptionError(null);
  }, []);

  // Don't render if no task
  if (!task) return null;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Edit Task">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title Input */}
        <div className="w-full">
          <label htmlFor="edit-task-title" className="block text-sm font-medium text-gray-700 mb-1.5">
            Title<span className="text-red-500 ml-1">*</span>
          </label>
          <input
            id="edit-task-title"
            name="title"
            type="text"
            value={title}
            onChange={handleTitleChange}
            onFocus={(e) => e.currentTarget.select()}
            placeholder="Enter task title"
            maxLength={200}
            required
            disabled={isSubmitting}
            autoFocus
            className={`w-full px-4 py-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 text-base min-h-[48px] ${
              titleError
                ? 'border-red-500 focus:ring-red-100 focus:border-red-500'
                : 'border-gray-300 focus:ring-indigo-100 focus:border-indigo-600'
            }`}
          />
          {titleError && (
            <p className="mt-1.5 text-sm text-red-600">{titleError}</p>
          )}
          <p className="mt-1.5 text-xs text-gray-500 text-right">{title.length}/200</p>
        </div>

        {/* Description Textarea */}
        <div className="w-full">
          <label htmlFor="edit-task-description" className="block text-sm font-medium text-gray-700 mb-1.5">
            Description
          </label>
          <textarea
            id="edit-task-description"
            name="description"
            value={description}
            onChange={handleDescriptionChange}
            onFocus={(e) => e.currentTarget.select()}
            placeholder="Enter task description (optional)"
            maxLength={1000}
            disabled={isSubmitting}
            rows={4}
            className={`w-full px-4 py-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 text-base resize-none ${
              descriptionError
                ? 'border-red-500 focus:ring-red-100 focus:border-red-500'
                : 'border-gray-300 focus:ring-indigo-100 focus:border-indigo-600'
            }`}
          />
          {descriptionError && (
            <p className="mt-1.5 text-sm text-red-600">{descriptionError}</p>
          )}
          <p className="mt-1.5 text-xs text-gray-500 text-right">{description.length}/1000</p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
            type="button"
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            type="submit"
            loading={isSubmitting}
            disabled={isSubmitting}
            aria-busy={isSubmitting}
          >
            Save Changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default memo(EditTaskModal);
