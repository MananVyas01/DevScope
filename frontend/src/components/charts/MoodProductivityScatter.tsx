'use client';

import { useEffect, useState } from 'react';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTheme } from 'next-themes';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

interface MoodProductivityScatterProps {
  useMockData: boolean;
}

const mockData = {
  datasets: [
    {
      label: 'High Focus',
      data: [
        { x: 4.5, y: 92 },
        { x: 4.2, y: 88 },
        { x: 4.8, y: 95 },
        { x: 4.3, y: 89 },
        { x: 4.7, y: 93 },
      ],
      backgroundColor: 'rgba(34, 197, 94, 0.8)',
      borderColor: 'rgb(34, 197, 94)',
      pointRadius: 6,
    },
    {
      label: 'Distracted',
      data: [
        { x: 2.1, y: 45 },
        { x: 2.5, y: 52 },
        { x: 2.8, y: 48 },
        { x: 2.2, y: 41 },
        { x: 2.6, y: 47 },
      ],
      backgroundColor: 'rgba(251, 191, 36, 0.8)',
      borderColor: 'rgb(251, 191, 36)',
      pointRadius: 6,
    },
    {
      label: 'Bug Fixing',
      data: [
        { x: 3.1, y: 68 },
        { x: 3.5, y: 72 },
        { x: 3.2, y: 70 },
        { x: 3.8, y: 75 },
        { x: 3.4, y: 71 },
      ],
      backgroundColor: 'rgba(239, 68, 68, 0.8)',
      borderColor: 'rgb(239, 68, 68)',
      pointRadius: 6,
    },
  ],
};

export default function MoodProductivityScatter({
  useMockData,
}: MoodProductivityScatterProps) {
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
      // TODO: Fetch real data from /stats/mood-productivity endpoint
      fetchMoodProductivityData();
    }
  }, [useMockData]);

  const fetchMoodProductivityData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stats/mood-productivity')
      // const data = await response.json()
      // setData(data)
      console.log('TODO: Implement /stats/mood-productivity endpoint');
    } catch (error) {
      console.error('Error fetching mood-productivity data:', error);
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
        callbacks: {
          title: () => '',
          label: (context: {
            dataset: { label: string };
            parsed: { x: number; y: number };
          }) => {
            const dataset = context.dataset.label;
            const mood = context.parsed.x;
            const productivity = context.parsed.y;
            return `${dataset}: Mood ${mood}/5, Productivity ${productivity}%`;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'linear' as const,
        position: 'bottom' as const,
        min: 1,
        max: 5,
        title: {
          display: true,
          text: 'Mood Score (1-5)',
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
          stepSize: 1,
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
      y: {
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'AI Productivity Score (%)',
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
        },
        ticks: {
          color: theme === 'dark' ? '#9CA3AF' : '#6B7280',
          callback: (value: string | number) => `${value}%`,
        },
        grid: {
          color: theme === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
    },
  };

  return (
    <div className="h-64">
      <Scatter data={data} options={options} />
    </div>
  );
}
