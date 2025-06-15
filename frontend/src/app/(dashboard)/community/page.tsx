'use client';

import { CommunityStatsCard } from '@/components/CommunityStatsCard';
import { TrendingUp, Users, Award, Globe } from 'lucide-react';

const mockCommunityData = {
  totalUsers: 12847,
  avgProductivityScore: 7.2,
  topLanguages: [
    { name: 'TypeScript', percentage: 34.2 },
    { name: 'Python', percentage: 28.1 },
    { name: 'JavaScript', percentage: 24.7 },
    { name: 'Go', percentage: 13.0 },
  ],
  userStats: {
    rank: 142,
    percentile: 88,
    productivityScore: 8.5,
    focusHours: 156,
    avgMood: 4.2,
  },
  weeklyTrends: {
    focusTime: '+12%',
    productivity: '+8%',
    mood: '+5%',
    participation: '+23%',
  },
};

export default function Community() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Community
        </h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Compare your productivity with developers worldwide and discover
          community trends.
        </p>
      </div>

      <div className="space-y-6">
        {/* Community Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Total Users
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {mockCommunityData.totalUsers.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Avg Productivity
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {mockCommunityData.avgProductivityScore}/10
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Award className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Your Rank
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  #{mockCommunityData.userStats.rank}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Globe className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Top Percentile
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {mockCommunityData.userStats.percentile}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Community Stats Card */}
        <CommunityStatsCard />

        {/* Weekly Trends */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Community Trends This Week
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {mockCommunityData.weeklyTrends.focusTime}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Focus Time
              </p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {mockCommunityData.weeklyTrends.productivity}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Productivity
              </p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {mockCommunityData.weeklyTrends.mood}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Mood Score
              </p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {mockCommunityData.weeklyTrends.participation}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Participation
              </p>
            </div>
          </div>
        </div>

        {/* Language Trends */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Popular Languages in Community
          </h3>
          <div className="space-y-4">
            {mockCommunityData.topLanguages.map((lang, index) => (
              <div
                key={lang.name}
                className="flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {index + 1}. {lang.name}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${lang.percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400 w-12">
                    {lang.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <Globe className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Privacy & Anonymity
              </h3>
              <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>
                  All community comparisons are completely anonymous. Your
                  personal data remains private, and only aggregated,
                  non-identifying metrics are used for community insights. You
                  can control what data is shared in your privacy settings.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
