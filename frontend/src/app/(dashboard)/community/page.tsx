'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/components/auth-provider';
import { Github, ExternalLink } from 'lucide-react';

interface GitHubUser {
  login: string;
  name: string;
  public_repos: number;
  followers: number;
  following: number;
  created_at: string;
  bio?: string;
  company?: string;
  location?: string;
  blog?: string;
}

interface GitHubRepo {
  name: string;
  language: string;
  stargazers_count: number;
  forks_count: number;
  updated_at: string;
  description?: string;
}

export default function Community() {
  const { user } = useAuth();
  const [githubUser, setGithubUser] = useState<GitHubUser | null>(null);
  const [githubRepos, setGithubRepos] = useState<GitHubRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.user_metadata?.user_name) {
      fetchGitHubData(user.user_metadata.user_name);
    } else {
      setLoading(false);
      setError('GitHub username not found in user profile');
    }
  }, [user]);

  const fetchGitHubData = async (username: string) => {
    try {
      setLoading(true);

      // Fetch user data
      const userResponse = await fetch(
        `https://api.github.com/users/${username}`
      );
      if (!userResponse.ok) throw new Error('Failed to fetch GitHub user data');
      const userData = await userResponse.json();
      setGithubUser(userData);

      // Fetch repositories
      const reposResponse = await fetch(
        `https://api.github.com/users/${username}/repos?sort=updated&per_page=10`
      );
      if (!reposResponse.ok)
        throw new Error('Failed to fetch GitHub repositories');
      const reposData = await reposResponse.json();
      setGithubRepos(reposData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to fetch GitHub data'
      );
    } finally {
      setLoading(false);
    }
  };

  const getLanguageStats = () => {
    const languageCounts: { [key: string]: number } = {};
    githubRepos.forEach(repo => {
      if (repo.language) {
        languageCounts[repo.language] =
          (languageCounts[repo.language] || 0) + 1;
      }
    });

    const total = Object.values(languageCounts).reduce(
      (sum, count) => sum + count,
      0
    );
    return Object.entries(languageCounts)
      .map(([language, count]) => ({
        name: language,
        percentage: total > 0 ? (count / total) * 100 : 0,
      }))
      .sort((a, b) => b.percentage - a.percentage)
      .slice(0, 5);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Github className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Unable to Load GitHub Data
          </h2>
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          GitHub Profile
        </h1>
        <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
          Your GitHub activity and repository statistics from real data.
        </p>
      </div>

      <div className="space-y-6">
        {/* GitHub Profile Overview */}
        {githubUser && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center space-x-4 mb-6">
              <img
                src={`https://github.com/${githubUser.login}.png`}
                alt={githubUser.name || githubUser.login}
                className="h-16 w-16 rounded-full"
              />
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {githubUser.name || githubUser.login}
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  @{githubUser.login}
                </p>
                {githubUser.bio && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {githubUser.bio}
                  </p>
                )}
                {githubUser.company && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    🏢 {githubUser.company}
                  </p>
                )}
                {githubUser.location && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    📍 {githubUser.location}
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {githubUser.public_repos}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Public Repos
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {githubUser.followers}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Followers
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {githubUser.following}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Following
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {new Date(githubUser.created_at).getFullYear()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Member Since
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Language Statistics */}
        {getLanguageStats().length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Your Programming Languages
            </h3>
            <div className="space-y-3">
              {getLanguageStats().map((lang, index) => (
                <div
                  key={lang.name}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        index === 0
                          ? 'bg-blue-500'
                          : index === 1
                            ? 'bg-green-500'
                            : index === 2
                              ? 'bg-yellow-500'
                              : index === 3
                                ? 'bg-purple-500'
                                : 'bg-gray-500'
                      }`}
                    ></div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {lang.name}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          index === 0
                            ? 'bg-blue-500'
                            : index === 1
                              ? 'bg-green-500'
                              : index === 2
                                ? 'bg-yellow-500'
                                : index === 3
                                  ? 'bg-purple-500'
                                  : 'bg-gray-500'
                        }`}
                        style={{ width: `${lang.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-400 w-12 text-right">
                      {lang.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Repositories */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Repositories
          </h3>
          <div className="space-y-4">
            {githubRepos.slice(0, 5).map(repo => (
              <div
                key={repo.name}
                className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {repo.name}
                      </h4>
                      <a
                        href={`https://github.com/${githubUser?.login}/${repo.name}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                    {repo.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {repo.description}
                      </p>
                    )}
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                      {repo.language && (
                        <span className="flex items-center space-x-1">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          <span>{repo.language}</span>
                        </span>
                      )}
                      <span>⭐ {repo.stargazers_count}</span>
                      <span>🍴 {repo.forks_count}</span>
                      <span>
                        Updated {new Date(repo.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
