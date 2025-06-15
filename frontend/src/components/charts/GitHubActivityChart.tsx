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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface GitHubActivityChartProps {
  useMockData: boolean;
}

const mockData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Pushes',
      data: [3, 2, 5, 4, 6, 1, 0],
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
    },
    {
      label: 'Pull Requests',
      data: [1, 0, 2, 1, 3, 0, 0],
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgb(34, 197, 94)',
      borderWidth: 1,
    },
  ],
};

export default function GitHubActivityChart({
  useMockData,
}: GitHubActivityChartProps) {
  const [data, setData] = useState(mockData);
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (useMockData) {
      setData(mockData);
    } else {
      // TODO: Fetch real data from /stats/github-activity endpoint
      fetchGitHubData();
    }
  }, [useMockData]);

  const fetchGitHubData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stats/github-activity')
      // const data = await response.json()
      // setData(data)
      console.log('TODO: Implement /stats/github-activity endpoint');
    } catch (error) {
      console.error('Error fetching GitHub activity data:', error);
      setData(mockData); // Fallback to mock data
    }
  };

  if (!mounted) {
    return (
      <div className="h-64 flex items-center justify-center">Loading...</div>
    );
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
          usePointStyle: true,
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
      y: {
        beginAtZero: true,
        stacked: false,
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
          stepSize: 1,
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
      <Bar data={data} options={options} />
    </div>
  );
}
