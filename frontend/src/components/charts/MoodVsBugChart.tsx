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

interface MoodVsBugChartProps {
  useMockData: boolean;
}

const mockData = {
  labels: ['Mood 1', 'Mood 2', 'Mood 3', 'Mood 4', 'Mood 5'],
  datasets: [
    {
      label: 'Bug-related Commits',
      data: [8, 6, 3, 2, 1],
      backgroundColor: [
        'rgba(239, 68, 68, 0.8)',
        'rgba(245, 101, 101, 0.8)',
        'rgba(251, 146, 60, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(59, 130, 246, 0.8)',
      ],
      borderColor: [
        'rgb(239, 68, 68)',
        'rgb(245, 101, 101)',
        'rgb(251, 146, 60)',
        'rgb(34, 197, 94)',
        'rgb(59, 130, 246)',
      ],
      borderWidth: 1,
    },
  ],
};

export default function MoodVsBugChart({ useMockData }: MoodVsBugChartProps) {
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
      // TODO: Fetch real data from /stats/mood-bug-correlation endpoint
      fetchMoodBugData();
    }
  }, [useMockData]);

  const fetchMoodBugData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stats/mood-bug-correlation')
      // const data = await response.json()
      // setData(data)
      console.log('TODO: Implement /stats/mood-bug-correlation endpoint');
    } catch (error) {
      console.error('Error fetching mood-bug correlation data:', error);
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
        display: false,
      },
      tooltip: {
        backgroundColor: theme === 'dark' ? '#374151' : '#ffffff',
        titleColor: theme === 'dark' ? '#ffffff' : '#000000',
        bodyColor: theme === 'dark' ? '#ffffff' : '#000000',
        borderColor: theme === 'dark' ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        callbacks: {
          title: (context: { label: string }[]) =>
            `Mood Score: ${context[0].label.split(' ')[1]}`,
          label: (context: { parsed: { y: number } }) =>
            `Bug Commits: ${context.parsed.y}`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Bug-related Commits',
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Mood Score (1-5)',
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
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
