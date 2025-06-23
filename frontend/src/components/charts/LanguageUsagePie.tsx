'use client';

import { useEffect, useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useTheme } from 'next-themes';
import { useAuth } from '@/components/auth-provider';

ChartJS.register(ArcElement, Tooltip, Legend);

interface GitHubRepo {
  language: string | null;
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label?: string;
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }>;
}

export default function LanguageUsagePie() {
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
      fetchGitHubLanguageData();
    }
  }, [mounted, user]);

  const fetchGitHubLanguageData = async () => {
    if (!user?.user_metadata?.user_name) {
      setError('GitHub username not found');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const username = user.user_metadata.user_name;

      // Fetch user's repositories
      const reposResponse = await fetch(
        `https://api.github.com/users/${username}/repos?sort=updated&per_page=50`
      );
      if (!reposResponse.ok) throw new Error('Failed to fetch repositories');
      const repos = await reposResponse.json(); // Count languages
      const languageCounts: { [key: string]: number } = {};
      repos.forEach((repo: GitHubRepo) => {
        if (repo.language && repo.language !== null) {
          languageCounts[repo.language] =
            (languageCounts[repo.language] || 0) + 1;
        }
      });

      // Convert to chart data
      const languages = Object.entries(languageCounts)
        .sort(([, a], [, b]) => (b as number) - (a as number))
        .slice(0, 6); // Top 6 languages

      if (languages.length === 0) {
        setData({
          labels: ['No Data'],
          datasets: [
            {
              label: 'Repositories',
              data: [1],
              backgroundColor: ['rgba(156, 163, 175, 0.8)'],
              borderColor: ['rgb(156, 163, 175)'],
              borderWidth: 2,
            },
          ],
        });
      } else {
        const colors = [
          'rgba(59, 130, 246, 0.8)', // Blue
          'rgba(34, 197, 94, 0.8)', // Green
          'rgba(251, 191, 36, 0.8)', // Yellow
          'rgba(139, 92, 246, 0.8)', // Purple
          'rgba(236, 72, 153, 0.8)', // Pink
          'rgba(245, 101, 101, 0.8)', // Red
        ];

        const borderColors = [
          'rgb(59, 130, 246)',
          'rgb(34, 197, 94)',
          'rgb(251, 191, 36)',
          'rgb(139, 92, 246)',
          'rgb(236, 72, 153)',
          'rgb(245, 101, 101)',
        ];

        setData({
          labels: languages.map(([lang]) => lang),
          datasets: [
            {
              label: 'Repositories',
              data: languages.map(([, count]) => count),
              backgroundColor: colors.slice(0, languages.length),
              borderColor: borderColors.slice(0, languages.length),
              borderWidth: 2,
            },
          ],
        });
      }
    } catch (err) {
      setError('Failed to fetch language data');
      console.error('Language data fetch error:', err);
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
            Connect your GitHub account to see languages
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
        position: 'bottom' as const,
        labels: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
          padding: 15,
          usePointStyle: true,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: theme === 'dark' ? '#374151' : '#ffffff',
        titleColor: theme === 'dark' ? '#ffffff' : '#000000',
        bodyColor: theme === 'dark' ? '#ffffff' : '#000000',
        borderColor: theme === 'dark' ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        callbacks: {
          label: (context: {
            label: string;
            parsed: number;
            dataset: { data: number[] };
          }) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce(
              (a: number, b: number) => a + b,
              0
            );
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${percentage}%`;
          },
        },
      },
    },
    cutout: '60%',
  };

  return (
    <div className="h-64">
      <Doughnut data={data} options={options} />
    </div>
  );
}
