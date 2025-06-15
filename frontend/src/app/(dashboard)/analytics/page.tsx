'use client';

import { useState } from 'react';
import { BarChart3, TrendingUp, Brain, Code, Heart } from 'lucide-react';
import WeeklyFocusChart from '@/components/charts/WeeklyFocusChart';
import MoodVsBugChart from '@/components/charts/MoodVsBugChart';
import LanguageUsagePie from '@/components/charts/LanguageUsagePie';
import GitHubActivityChart from '@/components/charts/GitHubActivityChart';
import MoodProductivityScatter from '@/components/charts/MoodProductivityScatter';
import StatsCard from '@/components/cards/StatsCard';

export default function AnalyticsPage() {
  const [useMockData, setUseMockData] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                Analytics Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Visualize your productivity patterns and developer insights
              </p>
            </div>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <input
                  type="checkbox"
                  checked={useMockData}
                  onChange={e => setUseMockData(e.target.checked)}
                  className="rounded"
                />
                Use Mock Data
              </label>
            </div>
          </div>
        </div>

        {/* Summary Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Focus Hours"
            value="42.5h"
            change="+12%"
            changeType="positive"
            icon={<TrendingUp className="h-5 w-5" />}
          />
          <StatsCard
            title="Avg Mood Score"
            value="4.2/5"
            change="+0.3"
            changeType="positive"
            icon={<Heart className="h-5 w-5" />}
          />
          <StatsCard
            title="Commits This Week"
            value="34"
            change="-5%"
            changeType="negative"
            icon={<Code className="h-5 w-5" />}
          />
          <StatsCard
            title="Productivity Score"
            value="87%"
            change="+15%"
            changeType="positive"
            icon={<Brain className="h-5 w-5" />}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Weekly Focus Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Weekly Focus Hours
            </h3>
            <WeeklyFocusChart useMockData={useMockData} />
          </div>

          {/* GitHub Activity Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              GitHub Activity
            </h3>
            <GitHubActivityChart useMockData={useMockData} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Language Usage Pie */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Language Usage
            </h3>
            <LanguageUsagePie useMockData={useMockData} />
          </div>

          {/* Mood vs Bug Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm lg:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Mood vs Bug Frequency
            </h3>
            <MoodVsBugChart useMockData={useMockData} />
          </div>
        </div>

        {/* Mood vs Productivity Scatter */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Mood vs AI Productivity Score
          </h3>
          <MoodProductivityScatter useMockData={useMockData} />
        </div>
      </div>
    </div>
  );
}
