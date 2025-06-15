'use client';

import React from 'react';
import { supabase } from './supabase';

// API base URL
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Types
export interface ActivityData {
  id?: string;
  activity_type: string;
  description?: string;
  duration_minutes: number;
  start_time: string;
  end_time?: string;
  tags?: string[];
  project_id?: string;
  synced?: boolean;
}

export interface MoodData {
  mood_score: number;
  energy_level: number;
  stress_level: number;
  notes?: string;
  tags?: string[];
}

export interface TimerSession {
  project_id?: string;
  activity_type: string;
  description?: string;
  duration_minutes: number;
  tags?: string[];
}

export interface SessionStats {
  totalSessions: number;
  totalFocusTime: number;
  totalBreakTime: number;
  averageSessionLength: number;
  todaySessions: number;
  todayFocusTime: number;
  streak: number;
}

// Network status hook
export function useNetworkStatus() {
  const [isOnline, setIsOnline] = React.useState(() => {
    if (typeof window !== 'undefined' && typeof navigator !== 'undefined') {
      return navigator.onLine;
    }
    return true;
  });

  React.useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

// API helper function
async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const session = await supabase.auth.getSession();
  const token = session.data.session?.access_token;

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// API functions
export const api = {
  // Activity endpoints
  async createActivity(activity: ActivityData) {
    return apiRequest('/timer/session/complete', {
      method: 'POST',
      body: JSON.stringify(activity),
    });
  },

  async getActivities(days = 30) {
    return apiRequest(`/activities?days=${days}`);
  },

  // Mood endpoints
  async createMood(mood: MoodData) {
    return apiRequest('/mood', {
      method: 'POST',
      body: JSON.stringify(mood),
    });
  },

  async getMoods(days = 30) {
    return apiRequest(`/mood?days=${days}`);
  },

  // Timer session endpoints
  async startTimer(session: TimerSession) {
    return apiRequest('/timer/start', {
      method: 'POST',
      body: JSON.stringify(session),
    });
  },

  async getTimerSession(sessionId: string) {
    return apiRequest(`/timer/session/${sessionId}`);
  },

  async pauseTimer(sessionId: string) {
    return apiRequest(`/timer/session/${sessionId}/pause`, {
      method: 'POST',
    });
  },

  async resumeTimer(sessionId: string) {
    return apiRequest(`/timer/session/${sessionId}/resume`, {
      method: 'POST',
    });
  },

  async completeTimer(sessionId: string) {
    return apiRequest(`/timer/session/${sessionId}/complete`, {
      method: 'POST',
    });
  },

  // Analytics endpoints
  async getAnalytics() {
    return apiRequest('/analytics/dashboard');
  },

  async getProductivityTrends(days = 30) {
    return apiRequest(`/analytics/productivity-trends?days=${days}`);
  },
};

// Offline storage utility
export class OfflineStorage {
  private static ACTIVITIES_KEY = 'devscope_activities';
  private static MOODS_KEY = 'devscope_moods';
  private static SESSIONS_KEY = 'devscope_sessions';

  // Check if localStorage is available
  private static isLocalStorageAvailable(): boolean {
    return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
  }

  // Activity storage
  static storeActivity(activity: ActivityData) {
    if (!this.isLocalStorageAvailable()) return;

    const stored = this.getStoredActivities();
    const activityWithId = {
      ...activity,
      id: activity.id || this.generateId(),
      synced: false,
    };
    stored.push(activityWithId);
    localStorage.setItem(this.ACTIVITIES_KEY, JSON.stringify(stored));
  }

  static getStoredActivities(): ActivityData[] {
    if (!this.isLocalStorageAvailable()) return [];

    const stored = localStorage.getItem(this.ACTIVITIES_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  // Mood storage
  static storeMood(mood: MoodData) {
    if (!this.isLocalStorageAvailable()) return;

    const stored = this.getStoredMoods();
    const moodWithId = {
      ...mood,
      id: this.generateId(),
      created_at: new Date().toISOString(),
      synced: false,
    };
    stored.push(moodWithId);
    localStorage.setItem(this.MOODS_KEY, JSON.stringify(stored));
  }

  static getStoredMoods(): (MoodData & {
    id: string;
    created_at: string;
    synced: boolean;
  })[] {
    if (!this.isLocalStorageAvailable()) return [];

    const stored = localStorage.getItem(this.MOODS_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  // Session storage
  static storeSession(session: SessionStats) {
    if (!this.isLocalStorageAvailable()) return;

    const stored = this.getStoredSessions();
    stored.push({
      ...session,
      id: this.generateId(),
      synced: false,
    });
    localStorage.setItem(this.SESSIONS_KEY, JSON.stringify(stored));
  }

  static getStoredSessions(): (SessionStats & {
    id: string;
    synced: boolean;
  })[] {
    if (!this.isLocalStorageAvailable()) return [];

    const stored = localStorage.getItem(this.SESSIONS_KEY);
    return stored ? JSON.parse(stored) : [];
  }

  // Sync functions
  static async syncActivities() {
    const activities = this.getStoredActivities().filter(a => !a.synced);

    for (const activity of activities) {
      try {
        await api.createActivity(activity);
        this.markActivityAsSynced(activity.id!);
      } catch (error) {
        console.error('Failed to sync activity:', error);
      }
    }
  }

  static async syncMoods() {
    const moods = this.getStoredMoods().filter(m => !m.synced);

    for (const mood of moods) {
      try {
        await api.createMood(mood);
        this.markMoodAsSynced(mood.id);
      } catch (error) {
        console.error('Failed to sync mood:', error);
      }
    }
  }

  static async syncAll() {
    try {
      await Promise.all([this.syncActivities(), this.syncMoods()]);

      console.log('Offline data synced successfully');
    } catch (error) {
      console.error('Failed to sync offline data:', error);
    }
  }

  // Helper functions
  private static markActivityAsSynced(id: string) {
    if (!this.isLocalStorageAvailable()) return;

    const activities = this.getStoredActivities();
    const updated = activities.map(a =>
      a.id === id ? { ...a, synced: true } : a
    );
    localStorage.setItem(this.ACTIVITIES_KEY, JSON.stringify(updated));
  }

  private static markMoodAsSynced(id: string) {
    if (!this.isLocalStorageAvailable()) return;

    const moods = this.getStoredMoods();
    const updated = moods.map(m => (m.id === id ? { ...m, synced: true } : m));
    localStorage.setItem(this.MOODS_KEY, JSON.stringify(updated));
  }

  static clearSyncedData() {
    if (!this.isLocalStorageAvailable()) return;

    // Remove synced items older than 7 days to prevent storage bloat
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 7);

    const activities = this.getStoredActivities().filter(
      a => !a.synced || new Date(a.start_time) > cutoffDate
    );
    localStorage.setItem(this.ACTIVITIES_KEY, JSON.stringify(activities));

    const moods = this.getStoredMoods().filter(
      m => !m.synced || new Date(m.created_at) > cutoffDate
    );
    localStorage.setItem(this.MOODS_KEY, JSON.stringify(moods));
  }

  private static generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  // Stats calculation from offline data
  static calculateStats(): SessionStats {
    const activities = this.getStoredActivities();
    const today = new Date().toDateString();

    let totalSessions = 0;
    let totalFocusTime = 0;
    let totalBreakTime = 0;
    let todaySessions = 0;
    let todayFocusTime = 0;

    activities.forEach(activity => {
      if (
        activity.tags?.includes('pomodoro') ||
        activity.tags?.includes('focus-session')
      ) {
        totalSessions++;
        const sessionDate = new Date(activity.start_time).toDateString();

        if (
          activity.activity_type === 'coding' ||
          activity.activity_type === 'focus'
        ) {
          totalFocusTime += activity.duration_minutes || 0;
          if (sessionDate === today) {
            todaySessions++;
            todayFocusTime += activity.duration_minutes || 0;
          }
        } else if (activity.activity_type === 'break') {
          totalBreakTime += activity.duration_minutes || 0;
        }
      }
    });

    const averageSessionLength =
      totalSessions > 0
        ? Math.round((totalFocusTime + totalBreakTime) / totalSessions)
        : 0;

    // Calculate streak (consecutive days with sessions)
    const streak = this.calculateStreak(activities);

    return {
      totalSessions,
      totalFocusTime,
      totalBreakTime,
      averageSessionLength,
      todaySessions,
      todayFocusTime,
      streak,
    };
  }

  private static calculateStreak(activities: ActivityData[]): number {
    const sessionDates = new Set(
      activities
        .filter(
          a => a.tags?.includes('pomodoro') || a.tags?.includes('focus-session')
        )
        .map(a => new Date(a.start_time).toDateString())
    );

    let streak = 0;
    const today = new Date();

    for (let i = 0; i < 365; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateString = date.toDateString();

      if (sessionDates.has(dateString)) {
        streak++;
      } else if (i > 0) {
        // Break in streak (ignore today if no sessions yet)
        break;
      }
    }

    return streak;
  }
}
