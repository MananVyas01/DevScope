/* eslint-disable no-undef */
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Play, Pause, RotateCcw, Coffee, Brain } from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { api, OfflineStorage, useNetworkStatus, type ActivityData } from '@/lib/api';
import MoodTrackerModal from '@/components/mood-tracker-modal';

type SessionType = 'focus' | 'break';
type SessionStatus = 'idle' | 'running' | 'paused';

interface ActivitySegment {
  start: number;
  end: number;
  isActive: boolean;
}

interface SessionData {
  id: string;
  type: SessionType;
  startTime: number;
  endTime?: number;
  duration: number;
  activeDuration: number;
  idleDuration: number;
  activitySegments: ActivitySegment[];
  status: 'completed' | 'paused' | 'cancelled';
}

export default function FocusTimer() {
  const { user } = useAuth();
  const isOnline = useNetworkStatus();

  // Timer state
  const [sessionType, setSessionType] = useState<SessionType>('focus');
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [currentSession, setCurrentSession] = useState<SessionData | null>(
    null
  );

  // Activity tracking
  const [isActive, setIsActive] = useState(true);
  const [activitySegments, setActivitySegments] = useState<ActivitySegment[]>(
    []
  );
  const lastActivityRef = useRef<number>(Date.now());
  const inactivityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const syncIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  // Mood tracker state
  const [showMoodTracker, setShowMoodTracker] = useState(false);
  const [completedSession, setCompletedSession] = useState<SessionData | null>(null);

  // Session durations
  const FOCUS_DURATION = 25 * 60;
  const BREAK_DURATION = 5 * 60;
  const INACTIVITY_THRESHOLD = 30 * 1000; // 30 seconds
  const SYNC_INTERVAL = 5 * 60 * 1000; // 5 minutes

  // Format time display
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const getProgress = () => {
    const totalDuration =
      sessionType === 'focus' ? FOCUS_DURATION : BREAK_DURATION;
    return ((totalDuration - timeLeft) / totalDuration) * 100;
  };

  // Activity tracking functions
  const markActive = useCallback(() => {
    const now = Date.now();
    lastActivityRef.current = now;

    if (!isActive) {
      setIsActive(true);
      // End the idle segment
      setActivitySegments(prev => {
        const lastSegment = prev[prev.length - 1];
        if (lastSegment && !lastSegment.isActive && !lastSegment.end) {
          return [...prev.slice(0, -1), { ...lastSegment, end: now }];
        }
        return prev;
      });
    }

    // Reset inactivity timer
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    inactivityTimerRef.current = setTimeout(() => {
      setIsActive(false);
      // Start a new idle segment
      setActivitySegments(prev => [
        ...prev,
        { start: Date.now(), end: 0, isActive: false },
      ]);
    }, INACTIVITY_THRESHOLD);
  }, [isActive]);

  // Set up activity listeners
  useEffect(() => {
    const events = ['mousemove', 'keydown', 'click', 'scroll'];

    events.forEach(event => {
      document.addEventListener(event, markActive, { passive: true });
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, markActive);
      });
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
    };
  }, [markActive]);

  // Sync offline data when coming back online
  useEffect(() => {
    if (isOnline && user) {
      OfflineStorage.syncAll().catch((error) => {
        console.error('Failed to sync offline data:', error);
      });
    }
  }, [isOnline, user]);

  // Sync offline data on component mount
  useEffect(() => {
    if (isOnline && user) {
      OfflineStorage.syncAll().catch((error) => {
        console.error('Failed to sync offline data on mount:', error);
      });
    }
  }, []);

  // Generate session ID
  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Calculate session statistics
  const calculateSessionStats = (segments: ActivitySegment[]) => {
    let activeDuration = 0;
    let idleDuration = 0;

    segments.forEach(segment => {
      const duration = (segment.end || Date.now()) - segment.start;
      if (segment.isActive) {
        activeDuration += duration;
      } else {
        idleDuration += duration;
      }
    });

    return { activeDuration, idleDuration };
  };

  // Start timer
  const startTimer = () => {
    if (status === 'idle') {
      // Create new session
      const now = Date.now();
      const newSession: SessionData = {
        id: generateSessionId(),
        type: sessionType,
        startTime: now,
        duration: sessionType === 'focus' ? FOCUS_DURATION : BREAK_DURATION,
        activeDuration: 0,
        idleDuration: 0,
        activitySegments: [{ start: now, end: 0, isActive: true }],
        status: 'completed',
      };

      setCurrentSession(newSession);
      setActivitySegments([{ start: now, end: 0, isActive: true }]);

      // Start sync interval
      syncIntervalRef.current = setInterval(() => {
        syncSessionData(newSession);
      }, SYNC_INTERVAL);
    }

    setStatus('running');

    // Start countdown
    intervalRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          // Session completed
          completeSession();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Pause timer
  const pauseTimer = () => {
    setStatus('paused');
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // End current activity segment
    const now = Date.now();
    setActivitySegments(prev => {
      const lastSegment = prev[prev.length - 1];
      if (lastSegment && !lastSegment.end) {
        return [...prev.slice(0, -1), { ...lastSegment, end: now }];
      }
      return prev;
    });
  };

  // Reset timer
  const resetTimer = () => {
    setStatus('idle');
    setTimeLeft(sessionType === 'focus' ? FOCUS_DURATION : BREAK_DURATION);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
    }

    // Cancel current session if exists
    if (currentSession) {
      cancelSession();
    }

    setCurrentSession(null);
    setActivitySegments([]);
  };

  // Complete session
  const completeSession = () => {
    if (!currentSession) return;

    const now = Date.now();
    const finalSegments = activitySegments.map(segment =>
      segment.end === 0 ? { ...segment, end: now } : segment
    );

    const stats = calculateSessionStats(finalSegments);

    const completedSession: SessionData = {
      ...currentSession,
      endTime: now,
      activeDuration: stats.activeDuration,
      idleDuration: stats.idleDuration,
      activitySegments: finalSegments,
      status: 'completed',
    };

    // Send final session data
    syncSessionData(completedSession, true);

    // Clear intervals
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (syncIntervalRef.current) clearInterval(syncIntervalRef.current);

    // Switch session type and reset
    const nextType = sessionType === 'focus' ? 'break' : 'focus';
    setSessionType(nextType);
    setTimeLeft(nextType === 'focus' ? FOCUS_DURATION : BREAK_DURATION);
    setStatus('idle');
    setCurrentSession(null);
    setActivitySegments([]);

    // Show mood tracker if focus session completed
    if (sessionType === 'focus') {
      showMoodTracker(completedSession);
    }
  };

  // Cancel session
  const cancelSession = () => {
    if (!currentSession) return;

    const now = Date.now();
    const finalSegments = activitySegments.map(segment =>
      segment.end === 0 ? { ...segment, end: now } : segment
    );

    const stats = calculateSessionStats(finalSegments);

    const cancelledSession: SessionData = {
      ...currentSession,
      endTime: now,
      activeDuration: stats.activeDuration,
      idleDuration: stats.idleDuration,
      activitySegments: finalSegments,
      status: 'cancelled',
    };

    // Send session data
    syncSessionData(cancelledSession, true);
  };

  // Sync session data to backend
  const syncSessionData = async (session: SessionData, isFinal = false) => {
    if (!user) return;

    try {
      const payload: ActivityData = {
        session_id: session.id,
        activity_type: session.type === 'focus' ? 'coding' : 'break',
        description: `${session.type} session`,
        duration_minutes: Math.round(session.activeDuration / 60000),
        idle_minutes: Math.round(session.idleDuration / 60000),
        start_time: new Date(session.startTime).toISOString(),
        end_time: session.endTime
          ? new Date(session.endTime).toISOString()
          : undefined,
        tags: [session.type, 'pomodoro'],
        metadata: {
          session_type: session.type,
          status: session.status,
          activity_segments: session.activitySegments.length,
          total_duration: session.duration,
        },
      };

      if (isOnline) {
        // Try to sync to backend
        await api.createActivity(payload);
        
        // If successful and we're online, try to sync any offline data
        if (isFinal) {
          await OfflineStorage.syncAll();
          OfflineStorage.clearSyncedData();
        }
      } else {
        // Store offline for later sync
        OfflineStorage.storeActivity(payload);
      }
    } catch (error) {
      void error; // Suppress unused variable warning

      // Store in offline storage for retry
      OfflineStorage.storeActivity({
        session_id: session.id,
        activity_type: session.type === 'focus' ? 'coding' : 'break',
        description: `${session.type} session`,
        duration_minutes: Math.round(session.activeDuration / 60000),
        idle_minutes: Math.round(session.idleDuration / 60000),
        start_time: new Date(session.startTime).toISOString(),
        end_time: session.endTime
          ? new Date(session.endTime).toISOString()
          : undefined,
        tags: [session.type, 'pomodoro'],
        metadata: {
          session_type: session.type,
          status: session.status,
          isFinal,
        },
      });
    }
  };

  // Show mood tracker modal
  // Show mood tracker modal
  const showMoodTracker = (session: SessionData) => {
    setCompletedSession(session);
    setShowMoodTracker(true);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Focus Timer
        </h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Use the Pomodoro technique to boost your productivity.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-8">
        <div className="text-center">
          {/* Session type indicator */}
          <div className="flex items-center justify-center mb-6">
            {sessionType === 'focus' ? (
              <div className="flex items-center text-blue-600 dark:text-blue-400">
                <Brain className="w-6 h-6 mr-2" />
                <span className="text-lg font-medium">Focus Session</span>
              </div>
            ) : (
              <div className="flex items-center text-green-600 dark:text-green-400">
                <Coffee className="w-6 h-6 mr-2" />
                <span className="text-lg font-medium">Break Time</span>
              </div>
            )}
          </div>

          {/* Circular progress indicator */}
          <div className="relative w-48 h-48 mx-auto mb-8">
            <svg
              className="w-48 h-48 transform -rotate-90"
              viewBox="0 0 100 100"
            >
              {/* Background circle */}
              <circle
                cx="50"
                cy="50"
                r="45"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                className="text-gray-200 dark:text-gray-700"
              />
              {/* Progress circle */}
              <circle
                cx="50"
                cy="50"
                r="45"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 45}`}
                strokeDashoffset={`${2 * Math.PI * 45 * (1 - getProgress() / 100)}`}
                className={
                  sessionType === 'focus' ? 'text-blue-600' : 'text-green-600'
                }
                style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
              />
            </svg>

            {/* Timer display */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 dark:text-white">
                  {formatTime(timeLeft)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {status === 'running'
                    ? 'Running'
                    : status === 'paused'
                      ? 'Paused'
                      : 'Ready'}
                </div>
              </div>
            </div>
          </div>

          {/* Activity and network status indicators */}
          <div className="mb-6 flex justify-center space-x-4">
            <div
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                isActive
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full mr-2 ${
                  isActive ? 'bg-green-500' : 'bg-yellow-500'
                }`}
              ></div>
              {isActive ? 'Active' : 'Idle'}
            </div>
            
            <div
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                isOnline
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full mr-2 ${
                  isOnline ? 'bg-blue-500' : 'bg-red-500'
                }`}
              ></div>
              {isOnline ? 'Online' : 'Offline'}
            </div>
          </div>

          {/* Control buttons */}
          <div className="flex justify-center space-x-4">
            {status === 'idle' && (
              <button
                onClick={startTimer}
                className="flex items-center bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                <Play className="w-5 h-5 mr-2" />
                Start
              </button>
            )}

            {status === 'running' && (
              <button
                onClick={pauseTimer}
                className="flex items-center bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                <Pause className="w-5 h-5 mr-2" />
                Pause
              </button>
            )}

            {status === 'paused' && (
              <button
                onClick={startTimer}
                className="flex items-center bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                <Play className="w-5 h-5 mr-2" />
                Resume
              </button>
            )}

            {status !== 'idle' && (
              <button
                onClick={resetTimer}
                className="flex items-center bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Reset
              </button>
            )}
          </div>

          {/* Session stats */}
          {currentSession && activitySegments.length > 0 && (
            <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                <div className="text-gray-600 dark:text-gray-400">
                  Active Time
                </div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {Math.round(
                    calculateSessionStats(activitySegments).activeDuration /
                      60000
                  )}
                  m
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                <div className="text-gray-600 dark:text-gray-400">
                  Idle Time
                </div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">
                  {Math.round(
                    calculateSessionStats(activitySegments).idleDuration / 60000
                  )}
                  m
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mood Tracker Modal */}
      <MoodTrackerModal
        isOpen={showMoodTracker}
        onClose={() => setShowMoodTracker(false)}
        sessionType={completedSession?.type || 'focus'}
        sessionDuration={completedSession?.activeDuration || 0}
      />
    </div>
  );
}
