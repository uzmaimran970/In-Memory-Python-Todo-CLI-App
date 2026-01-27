'use client';

import { useState, memo } from 'react';
import { Task } from '@/types';
import { toast } from 'react-hot-toast';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';

interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onReminderSet: (taskId: number, remindAt: string) => void;
}

function ReminderModal({ isOpen, onClose, task, onReminderSet }: ReminderModalProps) {
  const [reminderDate, setReminderDate] = useState('');
  const [reminderTime, setReminderTime] = useState('09:00');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Quick presets
  const presets = [
    { label: 'In 1 hour', getTime: () => new Date(Date.now() + 60 * 60 * 1000) },
    { label: 'Tomorrow 9AM', getTime: () => {
      const d = new Date();
      d.setDate(d.getDate() + 1);
      d.setHours(9, 0, 0, 0);
      return d;
    }},
    { label: 'In 3 days', getTime: () => new Date(Date.now() + 3 * 24 * 60 * 60 * 1000) },
    { label: 'Next week', getTime: () => new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) },
  ];

  const handlePreset = (getTime: () => Date) => {
    const d = getTime();
    setReminderDate(d.toISOString().split('T')[0]);
    setReminderTime(d.toTimeString().slice(0, 5));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task || !reminderDate || !reminderTime) return;

    const remindAt = new Date(`${reminderDate}T${reminderTime}:00`);
    if (remindAt <= new Date()) {
      toast.error('Reminder time must be in the future');
      return;
    }

    setIsSubmitting(true);
    try {
      await onReminderSet(task.id, remindAt.toISOString());
      toast.success('Reminder set successfully');
      onClose();
    } catch (error) {
      toast.error('Failed to set reminder');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!task) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Set Reminder">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Task info */}
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-500">Task:</p>
          <p className="font-medium text-gray-900">{task.title}</p>
        </div>

        {/* Quick presets */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Quick Set</label>
          <div className="grid grid-cols-2 gap-2">
            {presets.map((preset) => (
              <button
                key={preset.label}
                type="button"
                onClick={() => handlePreset(preset.getTime)}
                className="px-3 py-2 text-sm border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom date/time */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={reminderDate}
              onChange={(e) => setReminderDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              required
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-100 focus:border-indigo-600 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
            <input
              type="time"
              value={reminderTime}
              onChange={(e) => setReminderTime(e.target.value)}
              required
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-100 focus:border-indigo-600 text-sm"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={onClose} disabled={isSubmitting} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit" loading={isSubmitting} disabled={!reminderDate}>
            Set Reminder
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default memo(ReminderModal);
