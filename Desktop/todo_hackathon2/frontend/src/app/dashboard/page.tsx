'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
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
import ReminderModal from '@/components/tasks/ReminderModal';
import NotificationPanel from '@/components/notifications/NotificationPanel';
import Button from '@/components/ui/Button';
import { ChatbotIcon } from '@/components/chat';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isReminderModalOpen, setIsReminderModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [reminderTask, setReminderTask] = useState<Task | null>(null);
  const [highlightedTaskId, setHighlightedTaskId] = useState<number | null>(null);
  const [highlightType, setHighlightType] = useState<'create' | 'update' | null>(null);

  // Phase 5: Filter, sort, search state
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('created');
  const [priorityFilter, setPriorityFilter] = useState('all');

  // Phase 5: WebSocket real-time updates
  const [userId, setUserId] = useState<string | null>(null);

  const { isConnected, notifications, clearNotifications } = useWebSocket({
    userId,
    enabled: !!userId,
    onTaskCreated: () => refetchTasks(),
    onTaskUpdated: () => refetchTasks(),
    onTaskDeleted: () => refetchTasks(),
    onTaskCompleted: () => refetchTasks(),
  });

  const refetchTasks = useCallback(async () => {
    try {
      const fetchedTasks = await api.getTasks();
      setTasks(fetchedTasks);
    } catch (error) {
      console.error('[DASHBOARD] Error refetching tasks:', error);
    }
  }, []);

  // Fetch tasks on mount
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push('/login?error=session_expired');
      return;
    }

    // Extract user_id from JWT for WebSocket
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUserId(payload.sub || null);
    } catch { /* ignore */ }

    const fetchTasks = async () => {
      try {
        setIsLoading(true);
        const fetchedTasks = await api.getTasks();
        setTasks(fetchedTasks);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load tasks';
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [router]);

  // Phase 5: Client-side filtering, sorting, and search
  const filteredAndSortedTasks = useMemo(() => {
    let result = [...tasks];

    // Priority filter
    if (priorityFilter !== 'all') {
      result = result.filter(t => t.priority === priorityFilter);
    }

    // Search filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(t =>
        t.title.toLowerCase().includes(q) ||
        (t.description && t.description.toLowerCase().includes(q))
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'priority': {
          const order = { high: 0, medium: 1, low: 2 };
          return (order[a.priority as keyof typeof order] || 1) - (order[b.priority as keyof typeof order] || 1);
        }
        case 'due_date': {
          if (!a.due_date && !b.due_date) return 0;
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        }
        case 'created':
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

    return result;
  }, [tasks, priorityFilter, searchQuery, sortBy]);

  // Handle task toggle
  const handleTaskUpdate = useCallback((updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  }, []);

  const handleTaskEdit = useCallback((task: Task) => {
    setEditingTask(task);
    setIsEditModalOpen(true);
  }, []);

  const handleTaskDelete = useCallback((task: Task) => {
    setDeletingTask(task);
    setIsDeleteModalOpen(true);
  }, []);

  const handleTaskDeleted = useCallback((taskId: number) => {
    setTasks((prevTasks) => prevTasks.filter((t) => t.id !== taskId));
  }, []);

  const handleTaskCreated = useCallback((newTask: Task) => {
    setTasks((prevTasks) => [newTask, ...prevTasks]);
    setHighlightedTaskId(newTask.id);
    setHighlightType('create');
    setTimeout(() => { setHighlightedTaskId(null); setHighlightType(null); }, 2000);
  }, []);

  const handleTaskUpdated = useCallback((updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
    setHighlightedTaskId(updatedTask.id);
    setHighlightType('update');
    setTimeout(() => { setHighlightedTaskId(null); setHighlightType(null); }, 2000);
  }, []);

  // Phase 5: Reminder handler
  const handleReminderSet = useCallback(async (taskId: number, remindAt: string) => {
    try {
      const token = getAuthToken();
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/tasks/${taskId}/reminder`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ remind_at: remindAt }),
      });
      if (!res.ok) throw new Error('Failed to set reminder');
    } catch (error) {
      throw error;
    }
  }, []);

  const handleCloseCreateModal = useCallback(() => setIsCreateModalOpen(false), []);
  const handleCloseEditModal = useCallback(() => setIsEditModalOpen(false), []);

  const activeCount = tasks.filter((t) => !t.is_completed).length;
  const completedCount = tasks.filter((t) => t.is_completed).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        {/* Page Title + Actions */}
        <div className="mb-5 md:mb-6 flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-1 md:mb-2 truncate">
              My Tasks
            </h1>
            <p className="text-sm md:text-base text-gray-600">
              {activeCount} active, {completedCount} completed
            </p>
          </div>

          {/* Notifications + Add Button */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <NotificationPanel
              notifications={notifications}
              onClear={clearNotifications}
              isConnected={isConnected}
            />
            <div className="hidden sm:block">
              <Button
                variant="primary"
                onClick={() => setIsCreateModalOpen(true)}
                className="gap-2"
              >
                <Plus size={20} />
                <span>Add Task</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile FAB */}
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="sm:hidden fixed bottom-6 right-6 z-40 bg-indigo-600 text-white min-w-[56px] min-h-[56px] flex items-center justify-center rounded-full shadow-lg hover:bg-indigo-700 active:bg-indigo-800 transition-all"
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
            {/* Filters with Search/Sort/Priority */}
            <TaskFilters
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              sortBy={sortBy}
              onSortChange={setSortBy}
              priorityFilter={priorityFilter}
              onPriorityChange={setPriorityFilter}
            />

            {/* Task List */}
            <TaskList
              tasks={filteredAndSortedTasks}
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

      {/* Modals */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseCreateModal}
        onTaskCreated={handleTaskCreated}
      />
      <EditTaskModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        task={editingTask}
        onTaskUpdated={handleTaskUpdated}
      />
      <DeleteTaskModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        task={deletingTask}
        onTaskDeleted={handleTaskDeleted}
      />
      <ReminderModal
        isOpen={isReminderModalOpen}
        onClose={() => setIsReminderModalOpen(false)}
        task={reminderTask}
        onReminderSet={handleReminderSet}
      />

      <ChatbotIcon />
    </div>
  );
}
