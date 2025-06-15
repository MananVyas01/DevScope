'use client';

import { useState, useEffect, useCallback } from 'react';
import { TrendingUp, Users, Award, BarChart3 } from 'lucide-react';
import { useAuth } from '@/components/auth-provider';

interface CommunityStats {
  userRank: number;
  totalUsers: number;
  avgHours: number;
  userHours: number;
  topLanguages: { name: string; percentage: number }[];
  productivityScore: number;
  weeklyComparison: {
    hoursComparison: number; // percentage difference
    languageMatch: number; // percentage match with trending languages
  };
}

const mockCommunityStats: CommunityStats = {
  userRank: 234,
  totalUsers: 1247,
  avgHours: 6.8,
  userHours: 8.2,
  topLanguages: [
    { name: 'TypeScript', percentage: 35 },
    { name: 'Python', percentage: 28 },
    { name: 'JavaScript', percentage: 22 },
  ],
  productivityScore: 87,
  weeklyComparison: {
    hoursComparison: 20.5,
    languageMatch: 78,
  },
};

interface CommunityStatsCardProps {
  useMockData?: boolean;
}

export function CommunityStatsCard({
  useMockData = true,
}: CommunityStatsCardProps) {
  const [stats, setStats] = useState<CommunityStats>(mockCommunityStats);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const fetchCommunityStats = useCallback(async () => {
    if (!user) return;

    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/community/stats')
      // const data = await response.json()
      // setStats(data)
      console.log('TODO: Implement /api/community/stats endpoint');
      setStats(mockCommunityStats);
    } catch (error) {
      console.error('Error fetching community stats:', error);
      setStats(mockCommunityStats);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (useMockData) {
      setStats(mockCommunityStats);
    } else {
      fetchCommunityStats();
    }
  }, [useMockData, fetchCommunityStats]);

  const getComparisonText = (percentage: number) => {
    if (percentage > 0) {
      return `${percentage.toFixed(1)}% more productive than average`;
    } else {
      return `${Math.abs(percentage).toFixed(1)}% below average`;
    }
  };

  const getComparisonColor = (percentage: number) => {
    return percentage > 0
      ? 'text-green-600 dark:text-green-400'
      : 'text-red-600 dark:text-red-400';
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
          <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Community Insights
        </h3>
      </div>

      <div className="space-y-6">
        {/* Productivity Comparison */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Weekly Productivity
            </span>
            <div className="flex items-center gap-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span
                className={`text-sm font-medium ${getComparisonColor(stats.weeklyComparison.hoursComparison)}`}
              >
                {getComparisonText(stats.weeklyComparison.hoursComparison)}
              </span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {stats.userHours}h
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Community average: {stats.avgHours}h
          </div>
        </div>

        {/* Ranking */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Award className="h-4 w-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Your Rank
            </span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            #{stats.userRank}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            out of {stats.totalUsers.toLocaleString()} developers
          </div>
        </div>

        {/* Language Trends */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="h-4 w-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Trending Languages
            </span>
          </div>
          <div className="space-y-2">
            {stats.topLanguages.map((lang, index) => (
              <div
                key={lang.name}
                className="flex items-center justify-between"
              >
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {index + 1}. {lang.name}
                </span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {lang.percentage}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Language Match */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Language Trend Match
            </span>
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              {stats.weeklyComparison.languageMatch}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${stats.weeklyComparison.languageMatch}%` }}
            ></div>
          </div>
        </div>

        {/* Productivity Score */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
              {stats.productivityScore}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Productivity Score
            </div>
            <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              Based on focus time, commits, and community data
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
