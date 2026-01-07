'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { api, clearAuthToken } from '@/lib';
import { User } from '@/types';
import { LogOut, CheckSquare } from 'lucide-react';
import { toast } from '@/components/ui/Toast';

export default function Header() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user information on mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await api.getMe();
        setUser(userData);
      } catch (error) {
        // If we can't fetch user, redirect to login
        clearAuthToken();
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    // Clear authentication token
    clearAuthToken();

    // Show logout message
    toast.info('You have been logged out successfully');

    // Redirect to login page
    router.push('/login');
  };

  // Show loading state while fetching user
  if (isLoading) {
    return (
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2 md:gap-3">
              <div className="w-8 h-8 bg-gray-200 rounded animate-pulse" />
              <div className="w-16 md:w-24 h-5 md:h-6 bg-gray-200 rounded animate-pulse" />
            </div>
            <div className="w-16 md:w-20 h-9 md:h-10 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center gap-2 md:gap-3 min-w-0">
            <div className="flex items-center justify-center w-8 h-8 bg-indigo-600 rounded-lg flex-shrink-0">
              <CheckSquare size={20} className="text-white" aria-hidden="true" />
            </div>
            <h1 className="text-lg md:text-xl font-bold text-gray-900 truncate">
              <span className="hidden sm:inline">Todo App</span>
              <span className="sm:hidden">Todos</span>
            </h1>
          </div>

          {/* User Info and Logout */}
          <div className="flex items-center gap-2 md:gap-4">
            {user && (
              <div className="hidden md:flex flex-col items-end">
                {user.name && (
                  <span className="text-sm font-medium text-gray-900 truncate max-w-[150px] lg:max-w-[200px]">
                    {user.name}
                  </span>
                )}
                <span className="text-xs text-gray-500 truncate max-w-[150px] lg:max-w-[200px]">
                  {user.email}
                </span>
              </div>
            )}

            <Button
              variant="secondary"
              size="medium"
              onClick={handleLogout}
              className="flex items-center gap-2 text-sm md:text-base py-1.5 px-3 md:py-2.5 md:px-4 min-h-[40px]"
              aria-label="Logout"
            >
              <LogOut size={16} aria-hidden="true" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
