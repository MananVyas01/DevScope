'use client';

import { useEffect, useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useTheme } from 'next-themes';

ChartJS.register(ArcElement, Tooltip, Legend);

interface LanguageUsagePieProps {
  useMockData: boolean;
}

const mockData = {
  labels: ['TypeScript', 'Python', 'JavaScript', 'CSS', 'HTML'],
  datasets: [
    {
      label: 'Lines of Code',
      data: [45, 25, 15, 10, 5],
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(251, 191, 36, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)',
      ],
      borderColor: [
        'rgb(59, 130, 246)',
        'rgb(34, 197, 94)',
        'rgb(251, 191, 36)',
        'rgb(139, 92, 246)',
        'rgb(236, 72, 153)',
      ],
      borderWidth: 2,
    },
  ],
};

export default function LanguageUsagePie({
  useMockData,
}: LanguageUsagePieProps) {
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
      // TODO: Fetch real data from /stats/language-usage endpoint
      fetchLanguageData();
    }
  }, [useMockData]);

  const fetchLanguageData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stats/language-usage')
      // const data = await response.json()
      // setData(data)
      console.log('TODO: Implement /stats/language-usage endpoint');
    } catch (error) {
      console.error('Error fetching language usage data:', error);
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
