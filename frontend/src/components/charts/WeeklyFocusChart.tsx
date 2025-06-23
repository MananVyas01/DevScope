'use client';

import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { useTheme } from 'next-themes';
import { useAuth } from '@/components/auth-provider';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface GitHubCommit {
  commit: {
    committer: {
      date: string;
    };
  };
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
    fill?: boolean;
    pointRadius?: number;
    pointHoverRadius?: number;
  }>;
}

export default function WeeklyFocusChart() {
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

      // Fetch commit activity for the last 7 days
      const since = new Date();
      since.setDate(since.getDate() - 7);
      const sinceISO = since.toISOString();

      // Get commits from all user's repositories
      const reposResponse = await fetch(
        `https://api.github.com/users/${username}/repos?sort=pushed&per_page=10`
      );
      if (!reposResponse.ok) throw new Error('Failed to fetch repositories');
      const repos = await reposResponse.json();

      const dailyCommits: { [key: string]: number } = {};
      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

      // Initialize days with 0 commits
      for (let i = 0; i < 7; i++) {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        const dayName = days[date.getDay()];
        dailyCommits[dayName] = 0;
      }

      // Fetch commits for each repo (limit to avoid rate limits)
      for (const repo of repos.slice(0, 5)) {
        try {
          const commitsResponse = await fetch(
            `https://api.github.com/repos/${username}/${repo.name}/commits?since=${sinceISO}&author=${username}`
          );
          if (commitsResponse.ok) {
            const commits = await commitsResponse.json();

            commits.forEach((commit: GitHubCommit) => {
              const commitDate = new Date(commit.commit.committer.date);
              const dayName = days[commitDate.getDay()];
              if (dayName in dailyCommits) {
                dailyCommits[dayName]++;
              }
            });
          }
        } catch {
          console.log(`Could not fetch commits for ${repo.name}`);
        }
      }

      // Convert to chart data format
      const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      const dataValues = labels.map(day => {
        // Convert commits to estimated focus hours (rough approximation)
        const commits = dailyCommits[day] || 0;
        return Math.min(12, commits * 1.5 + Math.random() * 2); // 1.5h per commit + some variation
      });

      const chartData = {
        labels,
        datasets: [
          {
            label: 'Estimated Focus Hours',
            data: dataValues,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
          },
        ],
      };

      setData(chartData);
    } catch (err) {
      setError('Failed to fetch GitHub activity data');
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
          <p>{error || 'No data available'}</p>
          <p className="text-sm mt-1">
            Connect your GitHub account to see activity
          </p>
        </div>
      </div>
    );
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
      y: {
        beginAtZero: true,
        max: 10,
        ticks: {
          callback: (value: string | number) => `${value}h`,
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
      x: {
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
      <Line data={data} options={options} />
    </div>
  );
}
