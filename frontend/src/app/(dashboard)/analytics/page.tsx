'use client';

import { BarChart3, TrendingUp, Brain, Code, Heart } from 'lucide-react';
import WeeklyFocusChart from '@/components/charts/WeeklyFocusChart';
import MoodVsBugChart from '@/components/charts/MoodVsBugChart';
import LanguageUsagePie from '@/components/charts/LanguageUsagePie';
import GitHubActivityChart from '@/components/charts/GitHubActivityChart';
import MoodProductivityScatter from '@/components/charts/MoodProductivityScatter';
import StatsCard from '@/components/cards/StatsCard';
import { useAnalyticsData } from '@/hooks/useAnalyticsData';

export default function AnalyticsPage() {
  const { data: analyticsData, loading: analyticsLoading } = useAnalyticsData();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {' '}
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                Analytics Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Real-time insights from your GitHub activity and AI analysis
              </p>
            </div>
          </div>
        </div>{' '}
        {/* Summary Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {analyticsLoading ? (
            // Loading placeholders
            Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm animate-pulse"
              >
                <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ))
          ) : (
            <>
              {' '}
              <StatsCard
                title="Total Focus Hours"
                value={`${analyticsData?.totalFocusHours || 0}h`}
                change={`${(analyticsData?.changes?.focusHours || 0) > 0 ? '+' : ''}${(analyticsData?.changes?.focusHours || 0).toFixed(1)}%`}
                changeType={
                  (analyticsData?.changes?.focusHours || 0) > 0
                    ? 'positive'
                    : 'negative'
                }
                icon={<TrendingUp className="h-5 w-5" />}
              />
              <StatsCard
                title="Avg Mood Score"
                value={`${analyticsData?.avgMoodScore || 4.2}/5`}
                change={`${(analyticsData?.changes?.moodScore || 0) > 0 ? '+' : ''}${(analyticsData?.changes?.moodScore || 0).toFixed(1)}`}
                changeType={
                  (analyticsData?.changes?.moodScore || 0) > 0
                    ? 'positive'
                    : 'negative'
                }
                icon={<Heart className="h-5 w-5" />}
              />
              <StatsCard
                title="Commits This Week"
                value={`${analyticsData?.commitsThisWeek || 0}`}
                change={`${(analyticsData?.changes?.commits || 0) > 0 ? '+' : ''}${(analyticsData?.changes?.commits || 0).toFixed(0)}%`}
                changeType={
                  (analyticsData?.changes?.commits || 0) > 0
                    ? 'positive'
                    : 'negative'
                }
                icon={<Code className="h-5 w-5" />}
              />
              <StatsCard
                title="Productivity Score"
                value={`${analyticsData?.productivityScore?.toFixed(0) || 75}%`}
                change={`${(analyticsData?.changes?.productivity || 0) > 0 ? '+' : ''}${(analyticsData?.changes?.productivity || 0).toFixed(0)}%`}
                changeType={
                  (analyticsData?.changes?.productivity || 0) > 0
                    ? 'positive'
                    : 'negative'
                }
                icon={<Brain className="h-5 w-5" />}
              />
            </>
          )}
        </div>
        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Weekly Focus Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Weekly Focus Hours
            </h3>
            <WeeklyFocusChart useMockData={false} />
          </div>

          {/* GitHub Activity Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              GitHub Activity
            </h3>
            <GitHubActivityChart useMockData={false} />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Language Usage Pie */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Language Usage
            </h3>
            <LanguageUsagePie useMockData={false} />
          </div>

          {/* Mood vs Bug Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm lg:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Mood vs Bug Frequency
            </h3>
            <MoodVsBugChart useMockData={false} />
          </div>
        </div>
        {/* Mood vs Productivity Scatter */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Mood vs AI Productivity Score
          </h3>
          <MoodProductivityScatter useMockData={false} />
        </div>
      </div>
    </div>
  );
}
