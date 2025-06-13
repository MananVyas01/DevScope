import { useState, useEffect } from 'react';
import { OfflineStorage } from '@/lib/api';

interface SessionStats {
  totalSessions: number;
  totalFocusTime: number;
  totalBreakTime: number;
  averageSessionLength: number;
  todaySessions: number;
  todayFocusTime: number;
  streak: number;
}

export function useSessionStats() {
  const [stats, setStats] = useState<SessionStats>({
    totalSessions: 0,
    totalFocusTime: 0,
    totalBreakTime: 0,
    averageSessionLength: 0,
    todaySessions: 0,
    todayFocusTime: 0,
    streak: 0,
  });

  useEffect(() => {
    calculateStats();
  }, []);

  const calculateStats = () => {
    const activities = OfflineStorage.getStoredActivities();
    const today = new Date().toDateString();

    let totalSessions = 0;
    let totalFocusTime = 0;
    let totalBreakTime = 0;
    let todaySessions = 0;
    let todayFocusTime = 0;

    activities.forEach(activity => {
      if (activity.tags?.includes('pomodoro')) {
        totalSessions++;
        const sessionDate = new Date(activity.start_time).toDateString();

        if (activity.activity_type === 'coding') {
          totalFocusTime += activity.duration_minutes || 0;
          if (sessionDate === today) {
            todaySessions++;
            todayFocusTime += activity.duration_minutes || 0;
          }
        } else {
          totalBreakTime += activity.duration_minutes || 0;
        }
      }
    });

    const averageSessionLength =
      totalSessions > 0 ? totalFocusTime / totalSessions : 0;

    // Simple streak calculation (sessions today)
    const streak = todaySessions;

    setStats({
      totalSessions,
      totalFocusTime,
      totalBreakTime,
      averageSessionLength,
      todaySessions,
      todayFocusTime,
      streak,
    });
  };

  const refreshStats = () => {
    calculateStats();
  };

  return { stats, refreshStats };
}
