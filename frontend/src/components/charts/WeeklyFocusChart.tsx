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

interface WeeklyFocusChartProps {
  useMockData: boolean;
}

const mockData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Focus Hours',
      data: [6.5, 4.2, 8.1, 5.7, 7.3, 3.2, 2.1],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true,
    },
  ],
};

export default function WeeklyFocusChart({
  useMockData,
}: WeeklyFocusChartProps) {
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
      // TODO: Fetch real data from /stats/focus endpoint
      fetchFocusData();
    }
  }, [useMockData]);

  const fetchFocusData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stats/focus')
      // const data = await response.json()
      // setData(data)
      console.log('TODO: Implement /stats/focus endpoint');
    } catch (error) {
      console.error('Error fetching focus data:', error);
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
