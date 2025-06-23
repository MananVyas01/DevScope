'use client';

import { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTheme } from 'next-themes';
import { useAuth } from '@/components/auth-provider';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface GitHubEvent {
  type: string;
  created_at: string;
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
    borderWidth: number;
  }>;
}

export default function GitHubActivityChart() {
  const [data, setData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();
  const { user } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      fetchGitHubActivityData();
    }
  }, [mounted, user]);

  const fetchGitHubActivityData = async () => {
    if (!user?.user_metadata?.user_name) {
      setError('GitHub username not found');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const username = user.user_metadata.user_name;

      // Fetch user events from GitHub API
      const eventsResponse = await fetch(
        `https://api.github.com/users/${username}/events?per_page=100`
      );
      if (!eventsResponse.ok) throw new Error('Failed to fetch GitHub events');
      const events = await eventsResponse.json();

      // Process events from the last 7 days
      const now = new Date();
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

      const dailyActivity: { [key: string]: { pushes: number; prs: number } } =
        {};
      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

      // Initialize days
      for (let i = 0; i < 7; i++) {
        const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
        const dayKey = date.toISOString().split('T')[0];
        dailyActivity[dayKey] = { pushes: 0, prs: 0 };
      } // Count events
      events.forEach((event: GitHubEvent) => {
        const eventDate = new Date(event.created_at);
        if (eventDate >= sevenDaysAgo) {
          const dayKey = eventDate.toISOString().split('T')[0];
          if (dailyActivity[dayKey]) {
            if (event.type === 'PushEvent') {
              dailyActivity[dayKey].pushes++;
            } else if (event.type === 'PullRequestEvent') {
              dailyActivity[dayKey].prs++;
            }
          }
        }
      });

      // Convert to chart format
      const sortedDays = Object.keys(dailyActivity).sort();
      const labels = sortedDays.map(dateStr => {
        const date = new Date(dateStr);
        return days[date.getDay()];
      });
      const pushData = sortedDays.map(dateStr => dailyActivity[dateStr].pushes);
      const prData = sortedDays.map(dateStr => dailyActivity[dateStr].prs);

      setData({
        labels,
        datasets: [
          {
            label: 'Pushes',
            data: pushData,
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: 'rgb(59, 130, 246)',
            borderWidth: 1,
          },
          {
            label: 'Pull Requests',
            data: prData,
            backgroundColor: 'rgba(34, 197, 94, 0.8)',
            borderColor: 'rgb(34, 197, 94)',
            borderWidth: 1,
          },
        ],
      });
    } catch (err) {
      setError('Failed to fetch GitHub activity');
      console.error('GitHub activity fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) {
    return (
      <div className="h-64 flex items-center justify-center">Loading...</div>
    );
  }

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p>{error || 'No activity data available'}</p>
          <p className="text-sm mt-1">GitHub activity will appear here</p>
        </div>
      </div>
    );
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: theme === 'dark' ? '#ffffff' : '#000000',
        },
      },
      tooltip: {
        backgroundColor: theme === 'dark' ? '#374151' : '#ffffff',
        titleColor: theme === 'dark' ? '#ffffff' : '#000000',
        bodyColor: theme === 'dark' ? '#ffffff' : '#000000',
        borderColor: theme === 'dark' ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
      y: {
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Bar data={data} options={options} />
    </div>
  );
}
