'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Task, FilterType } from '@/types';
import { api } from '@/lib/api';
import { getAuthToken } from '@/lib/auth';
import { toast } from 'react-hot-toast';
import { Plus } from 'lucide-react';
import Header from '@/components/layout/Header';
import TaskFilters from '@/components/tasks/TaskFilters';
import TaskList from '@/components/tasks/TaskList';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import CreateTaskModal from '@/components/tasks/CreateTaskModal';
import EditTaskModal from '@/components/tasks/EditTaskModal';
import DeleteTaskModal from '@/components/tasks/DeleteTaskModal';
import Button from '@/components/ui/Button';

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [highlightedTaskId, setHighlightedTaskId] = useState<number | null>(null);
  const [highlightType, setHighlightType] = useState<'create' | 'update' | null>(null);

  // Fetch tasks on mount
  useEffect(() => {
    console.log('[DASHBOARD] Component mounted');

    // Check for auth token first
    const token = getAuthToken();
    if (!token) {
      console.warn('[DASHBOARD] No auth token found! Redirecting to login...');
      router.push('/login?error=session_expired');
      return;
    }

    console.log('[DASHBOARD] Auth token found, fetching tasks...');

    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        console.log('[DASHBOARD] Calling api.getTasks()...');
        const fetchedTasks = await api.getTasks();
        console.log('[DASHBOARD] Tasks fetched successfully:', { count: fetchedTasks.length });
        setTasks(fetchedTasks);
      } catch (error) {
        console.error('[DASHBOARD] Error fetching tasks:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load tasks';
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [router]);

  // Handle task toggle (completion status) - receives updated task from TaskCard
  const handleTaskUpdate = useCallback((updatedTask: Task) => {
    // Update task in the list with the new data from server
    setTasks((prevTasks) =>
      prevTasks.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  }, []);

  // Handle task edit - open edit modal
  const handleTaskEdit = useCallback((task: Task) => {
    setEditingTask(task);
    setIsEditModalOpen(true);
  }, []);

  // Handle task delete - open delete modal
  const handleTaskDelete = useCallback((task: Task) => {
    setDeletingTask(task);
    setIsDeleteModalOpen(true);
  }, []);

  // Handle task deletion confirmation
  const handleTaskDeleted = useCallback((taskId: number) => {
    // Remove task from tasks array
    setTasks((prevTasks) => prevTasks.filter((t) => t.id !== taskId));
  }, []);

  // Handle task creation
  const handleTaskCreated = useCallback((newTask: Task) => {
    // Add new task to the beginning of the list (newest first)
    setTasks((prevTasks) => [newTask, ...prevTasks]);

    // Highlight the new task temporarily with emerald color
    setHighlightedTaskId(newTask.id);
    setHighlightType('create');

    // Remove highlight after animation
    setTimeout(() => {
      setHighlightedTaskId(null);
      setHighlightType(null);
    }, 2000);
  }, []);

  // Handle task update - update task in list and highlight
  const handleTaskUpdated = useCallback((updatedTask: Task) => {
    // Update task in the list
    setTasks((prevTasks) =>
      prevTasks.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );

    // Highlight the updated task temporarily with indigo color
    setHighlightedTaskId(updatedTask.id);
    setHighlightType('update');

    // Remove highlight after animation
    setTimeout(() => {
      setHighlightedTaskId(null);
      setHighlightType(null);
    }, 2000);
  }, []);

  // Memoized modal close handlers to prevent re-renders
  const handleCloseCreateModal = useCallback(() => {
    setIsCreateModalOpen(false);
  }, []);

  const handleCloseEditModal = useCallback(() => {
    setIsEditModalOpen(false);
  }, []);

  // Compute statistics
  const activeCount = tasks.filter((t) => !t.is_completed).length;
  const completedCount = tasks.filter((t) => t.is_completed).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        {/* Page Title, Statistics, and Add Task Button */}
        <div className="mb-5 md:mb-6 flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-1 md:mb-2 truncate">
              My Tasks
            </h1>
            <p className="text-sm md:text-base text-gray-600">
              {activeCount} active, {completedCount} completed
            </p>
          </div>

          {/* Add Task Button - Desktop */}
          <div className="hidden sm:block flex-shrink-0">
            <Button
              variant="primary"
              onClick={() => setIsCreateModalOpen(true)}
              className="gap-2"
              aria-label="Create new task"
            >
              <Plus size={20} />
              <span>Add Task</span>
            </Button>
          </div>
        </div>

        {/* Add Task Button - Mobile (Floating Action Button) */}
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="sm:hidden fixed bottom-6 right-6 z-40 bg-indigo-600 text-white min-w-[56px] min-h-[56px] flex items-center justify-center rounded-full shadow-lg hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-100 active:bg-indigo-800 transition-all duration-200"
          aria-label="Create new task"
        >
          <Plus size={24} />
        </button>

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <LoadingSkeleton height="h-10" width="w-20" />
              <LoadingSkeleton height="h-10" width="w-20" />
              <LoadingSkeleton height="h-10" width="w-28" />
            </div>
            <div className="space-y-3">
              <LoadingSkeleton count={5} height="h-24" />
            </div>
          </div>
        ) : (
          <>
            {/* Filters */}
            <TaskFilters
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
            />

            {/* Task List */}
            <TaskList
              tasks={tasks}
              filter={activeFilter}
              onTaskUpdate={handleTaskUpdate}
              onTaskEdit={handleTaskEdit}
              onTaskDelete={handleTaskDelete}
              highlightedTaskId={highlightedTaskId}
              highlightType={highlightType}
            />
          </>
        )}
      </main>

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseCreateModal}
        onTaskCreated={handleTaskCreated}
      />

      {/* Edit Task Modal */}
      <EditTaskModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        task={editingTask}
        onTaskUpdated={handleTaskUpdated}
      />

      {/* Delete Task Modal */}
      <DeleteTaskModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        task={deletingTask}
        onTaskDeleted={handleTaskDeleted}
      />
    </div>
  );
}
