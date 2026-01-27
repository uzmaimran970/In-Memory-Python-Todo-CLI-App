'use client';

import { useState, memo } from 'react';
import { WebSocketMessage } from '@/lib/websocket';

interface NotificationPanelProps {
  notifications: WebSocketMessage[];
  onClear: () => void;
  isConnected: boolean;
}

function NotificationPanel({ notifications, onClear, isConnected }: NotificationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const unreadCount = notifications.length;

  return (
    <div className="relative">
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-indigo-600 transition-colors rounded-lg hover:bg-gray-100"
        title={isConnected ? 'Notifications (live)' : 'Notifications (offline)'}
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}

        {/* Connection indicator */}
        <span className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white ${
          isConnected ? 'bg-green-400' : 'bg-gray-400'
        }`} />
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
            <div className="flex items-center gap-2">
              {notifications.length > 0 && (
                <button
                  onClick={onClear}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Clear all
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Notification List */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <svg className="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <p className="text-sm text-gray-500">No notifications yet</p>
                <p className="text-xs text-gray-400 mt-1">
                  {isConnected ? 'Connected for live updates' : 'Connecting...'}
                </p>
              </div>
            ) : (
              notifications.map((notification, index) => (
                <div
                  key={index}
                  className="px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${
                      notification.notification_type === 'reminder' ? 'bg-yellow-400' :
                      notification.type === 'task.completed' ? 'bg-green-400' :
                      'bg-indigo-400'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {notification.title || getNotificationTitle(notification)}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {notification.body || getNotificationBody(notification)}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatTime(notification.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
            <p className="text-xs text-gray-500 text-center">
              {isConnected ? (
                <span className="text-green-600">Live updates active</span>
              ) : (
                <span className="text-gray-400">Reconnecting...</span>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function getNotificationTitle(msg: WebSocketMessage): string {
  switch (msg.type) {
    case 'task.created': return 'Task Created';
    case 'task.updated': return 'Task Updated';
    case 'task.deleted': return 'Task Deleted';
    case 'task.completed': return 'Task Completed';
    case 'notification': return msg.title || 'Notification';
    default: return 'Update';
  }
}

function getNotificationBody(msg: WebSocketMessage): string {
  const payload = msg.payload as Record<string, string> | undefined;
  if (payload?.title) return payload.title;
  if (msg.body) return msg.body;
  return 'A task was updated';
}

function formatTime(timestamp?: string): string {
  if (!timestamp) return 'Just now';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

export default memo(NotificationPanel);
