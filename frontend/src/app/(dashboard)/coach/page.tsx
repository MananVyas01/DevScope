'use client';

import { useState, useEffect } from 'react';
import { Brain, Target, Calendar, Star } from 'lucide-react';
import { useAuth } from '@/components/auth-provider';

interface AIReview {
  id: string;
  summary: string;
  suggestions: string[];
  tags: string[];
  productivity_score: number;
  reviewed_at: string;
  git_stats?: {
    commits: number;
    files_changed: number;
    lines_added: number;
    lines_deleted: number;
  };
}

const mockReviews: AIReview[] = [
  {
    id: '1',
    summary:
      'Today, you worked on implementing the Community Mode and Privacy Controls features. You made significant progress on the settings page and dashboard layout, showing strong focus on user experience and data privacy.',
    suggestions: [
      'Consider adding unit tests for the new privacy control components to ensure data handling is secure.',
      'The Community Mode toggle logic could benefit from more granular error handling.',
      'Documentation for the new privacy features would help future maintenance.',
    ],
    tags: ['#feature', '#privacy', '#ui-components', '#settings'],
    productivity_score: 8,
    reviewed_at: '2025-06-15T18:30:00Z',
    git_stats: {
      commits: 6,
      files_changed: 8,
      lines_added: 247,
      lines_deleted: 31,
    },
  },
  {
    id: '2',
    summary:
      'Yesterday focused on analytics dashboard implementation with comprehensive chart components. Strong technical execution with Chart.js integration and responsive design patterns.',
    suggestions: [
      'Chart performance could be optimized with data memoization for large datasets.',
      'Consider extracting common chart configuration into a shared utility.',
      'Add accessibility features like keyboard navigation for chart interactions.',
    ],
    tags: ['#analytics', '#charts', '#performance', '#a11y'],
    productivity_score: 9,
    reviewed_at: '2025-06-14T19:15:00Z',
    git_stats: {
      commits: 4,
      files_changed: 12,
      lines_added: 324,
      lines_deleted: 18,
    },
  },
  {
    id: '3',
    summary:
      'Two days ago concentrated on focus timer functionality and mood tracking integration. Good progress on state management and user interaction patterns.',
    suggestions: [
      'Timer state transitions could use more comprehensive testing scenarios.',
      'Mood data persistence needs validation and error recovery mechanisms.',
      'Consider implementing timer session recovery for unexpected interruptions.',
    ],
    tags: ['#timer', '#state-management', '#testing', '#ux'],
    productivity_score: 7,
    reviewed_at: '2025-06-13T17:45:00Z',
    git_stats: {
      commits: 3,
      files_changed: 5,
      lines_added: 156,
      lines_deleted: 42,
    },
  },
];

export default function AICoach() {
  const [reviews] = useState<AIReview[]>(mockReviews);
  const [loading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    // In a real app, fetch reviews from API
    // fetchAIReviews();
  }, [user]);

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 dark:text-green-400';
    if (score >= 6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8) return '🚀';
    if (score >= 6) return '📈';
    return '💡';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Brain className="h-8 w-8 text-purple-600" />
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            AI Code Coach
          </h1>
        </div>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          Daily AI-powered insights about your development activity and
          productivity patterns.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Latest Review Highlight */}
          {reviews[0] && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-2xl">
                      {getScoreIcon(reviews[0].productivity_score)}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Latest Daily Review
                    </h3>
                    <span
                      className={`text-xl font-bold ${getScoreColor(reviews[0].productivity_score)}`}
                    >
                      {reviews[0].productivity_score}/10
                    </span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">
                    {reviews[0].summary}
                  </p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {reviews[0].tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  {reviews[0].git_stats && (
                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          {reviews[0].git_stats.commits}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Commits
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">
                          {reviews[0].git_stats.files_changed}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Files
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-green-600 dark:text-green-400">
                          +{reviews[0].git_stats.lines_added}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Added
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-red-600 dark:text-red-400">
                          -{reviews[0].git_stats.lines_deleted}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Removed
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Review History */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                Review History
              </h3>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {reviews.map(review => (
                <div
                  key={review.id}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-lg">
                          {getScoreIcon(review.productivity_score)}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {formatDate(review.reviewed_at)}
                        </span>
                        <span
                          className={`text-sm font-medium ${getScoreColor(review.productivity_score)}`}
                        >
                          Score: {review.productivity_score}/10
                        </span>
                      </div>
                      <p className="text-gray-800 dark:text-gray-200 mb-3 text-sm leading-relaxed">
                        {review.summary}
                      </p>
                      <div className="space-y-2 mb-3">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                          <Target className="h-4 w-4 mr-1" />
                          Suggestions:
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400 ml-5">
                          {review.suggestions.map((suggestion, index) => (
                            <li key={index}>{suggestion}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {review.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Generate Review Button */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="text-center">
              <Brain className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Generate New Review
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Analyze your latest git activity and get AI-powered insights.
              </p>
              <button
                onClick={() => {
                  // TODO: Implement manual review generation
                  console.log('Generate new review');
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                <Star className="h-4 w-4 mr-2" />
                Generate Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
