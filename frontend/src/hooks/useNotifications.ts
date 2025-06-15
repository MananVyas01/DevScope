import { useEffect } from 'react';

export function useNotifications() {
  useEffect(() => {
    // Request notification permission on component mount
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const showNotification = (title: string, options?: NotificationOptions) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        ...options,
      });
    }
  };

  const showSessionComplete = (
    sessionType: 'focus' | 'break',
    duration: number
  ) => {
    const title =
      sessionType === 'focus'
        ? '🎯 Focus Session Complete!'
        : '☕ Break Time Over!';

    const message =
      sessionType === 'focus'
        ? `Great work! You focused for ${Math.round(duration / 60)} minutes. Time for a break!`
        : `Break's over! Ready for another focus session?`;

    showNotification(title, {
      body: message,
      tag: 'session-complete',
      requireInteraction: true,
      actions: [
        {
          action: 'start-next',
          title: sessionType === 'focus' ? 'Start Break' : 'Start Focus',
        },
        { action: 'dismiss', title: 'Dismiss' },
      ],
    });
  };

  const showActivityReminder = () => {
    showNotification('💤 You seem idle', {
      body: 'Take a moment to stretch or adjust your posture!',
      tag: 'activity-reminder',
    });
  };

  return {
    showNotification,
    showSessionComplete,
    showActivityReminder,
    isSupported: 'Notification' in window,
    permission:
      typeof window !== 'undefined' && 'Notification' in window
        ? Notification.permission
        : 'denied',
  };
}
