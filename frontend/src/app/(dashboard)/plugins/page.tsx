'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  Package, 
  Plus, 
  Download, 
  Trash2, 
  Power, 
  PowerOff,
  Github,
  Search,
  Filter,
  AlertCircle,
  CheckCircle,
  Globe
} from 'lucide-react';
import { useAuth } from '@/components/auth-provider';
import { pluginManager, type InstalledPlugin } from '@/lib/plugin-manager';

interface PluginCardProps {
  plugin: InstalledPlugin;
  onToggle: (_pluginId: string, _enabled: boolean) => void;
  onUninstall: (_pluginId: string) => void;
}

function PluginCard({ plugin, onToggle, onUninstall }: PluginCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    await onToggle(plugin.id, !plugin.enabled);
    setIsLoading(false);
  };

  const handleUninstall = async () => {
    if (window.confirm(`Are you sure you want to uninstall "${plugin.manifest.name}"?`)) {
      setIsLoading(true);
      await onUninstall(plugin.id);
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {plugin.manifest.icon ? (
            <div
              style={{ 
                backgroundImage: `url(${plugin.manifest.icon})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
              className="w-10 h-10 rounded-lg"
            />
          ) : (
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Package className="h-5 w-5 text-white" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {plugin.manifest.name}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              v{plugin.manifest.version}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleToggle}
            disabled={isLoading}
            className={`p-2 rounded-md transition-colors ${
              plugin.enabled
                ? 'bg-green-100 text-green-600 hover:bg-green-200 dark:bg-green-900/20 dark:text-green-400'
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-500'
            }`}
            title={plugin.enabled ? 'Disable plugin' : 'Enable plugin'}
          >
            {plugin.enabled ? <Power className="h-4 w-4" /> : <PowerOff className="h-4 w-4" />}
          </button>
          <button
            onClick={handleUninstall}
            disabled={isLoading}
            className="p-2 rounded-md text-red-600 hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors"
            title="Uninstall plugin"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4">
        {plugin.manifest.description}
      </p>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {plugin.manifest.category && (
          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs rounded-full">
            {plugin.manifest.category}
          </span>
        )}
        {plugin.manifest.tags?.map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full"
          >
            {tag}
          </span>
        ))}
      </div>
      
      <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <span>
          Installed {new Date(plugin.installed_at).toLocaleDateString()}
        </span>
        <div className="flex items-center space-x-2">
          {plugin.manifest.homepage && (
            <a
              href={plugin.manifest.homepage}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              <Globe className="h-4 w-4" />
            </a>
          )}
          {plugin.manifest.repository && (
            <a
              href={plugin.manifest.repository}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-700 dark:hover:text-gray-300"
            >
              <Github className="h-4 w-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PluginMarketplace() {
  const [plugins, setPlugins] = useState<InstalledPlugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState(false);
  const [githubUrl, setGithubUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const { user } = useAuth();

  const loadPlugins = useCallback(async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const installedPlugins = await pluginManager.getInstalledPlugins(user.id);
      setPlugins(installedPlugins);
    } catch (error) {
      console.error('Failed to load plugins:', error);
      setError('Failed to load installed plugins');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadPlugins();
  }, [loadPlugins]);

  const handleInstallFromGitHub = async () => {
    if (!githubUrl.trim() || !user) return;
    
    setInstalling(true);
    setError(null);
    setSuccess(null);
    
    try {
      const manifest = await pluginManager.fetchManifestFromGitHub(githubUrl);
      const plugin = await pluginManager.installPlugin(manifest, user.id);
      
      setPlugins(prev => [...prev, plugin]);
      setGithubUrl('');
      setSuccess(`Successfully installed "${plugin.manifest.name}"`);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to install plugin');
    } finally {
      setInstalling(false);
    }
  };

  const handleTogglePlugin = async (pluginId: string, enabled: boolean) => {
    try {
      await pluginManager.togglePlugin(pluginId, enabled);
      setPlugins(prev => 
        prev.map(p => p.id === pluginId ? { ...p, enabled } : p)
      );
    } catch {
      setError('Failed to toggle plugin');
    }
  };

  const handleUninstallPlugin = async (pluginId: string) => {
    try {
      await pluginManager.uninstallPlugin(pluginId);
      setPlugins(prev => prev.filter(p => p.id !== pluginId));
      setSuccess('Plugin uninstalled successfully');
    } catch {
      setError('Failed to uninstall plugin');
    }
  };

  const filteredPlugins = plugins.filter(plugin => {
    const matchesSearch = plugin.manifest.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plugin.manifest.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || plugin.manifest.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...new Set(plugins.map(p => p.manifest.category).filter(Boolean))];

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <Package className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Plugin Marketplace
          </h1>
        </div>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          Extend DevScope with third-party plugins to enhance your development workflow.
        </p>
      </div>

      {/* Install New Plugin */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Install Plugin from GitHub
        </h3>
        
        <div className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username/plugin-repo"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              disabled={installing}
            />
          </div>
          <button
            onClick={handleInstallFromGitHub}
            disabled={installing || !githubUrl.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {installing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
            ) : (
              <Download className="h-4 w-4 mr-2" />
            )}
            Install
          </button>
        </div>
        
        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md flex items-center">
            <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 mr-2" />
            <span className="text-sm text-red-800 dark:text-red-300">{error}</span>
          </div>
        )}
        
        {success && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md flex items-center">
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400 mr-2" />
            <span className="text-sm text-green-800 dark:text-green-300">{success}</span>
          </div>
        )}
      </div>

      {/* Search and Filter */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search plugins..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="pl-10 pr-8 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Plugins List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredPlugins.length === 0 ? (
        <div className="text-center py-12">
          <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {plugins.length === 0 ? 'No plugins installed' : 'No plugins found'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {plugins.length === 0 
              ? 'Install your first plugin from GitHub to get started.'
              : 'Try adjusting your search or filter criteria.'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlugins.map((plugin) => (
            <PluginCard
              key={plugin.id}
              plugin={plugin}
              onToggle={handleTogglePlugin}
              onUninstall={handleUninstallPlugin}
            />
          ))}
        </div>
      )}

      {/* Plugin Development Info */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2 flex items-center">
          <Github className="h-5 w-5 mr-2" />
          Develop Your Own Plugin
        </h3>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Create custom plugins to extend DevScope&apos;s functionality. Your plugin needs a 
          <code className="mx-1 px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm">devscope-plugin.json</code> 
          manifest file in the repository root.
        </p>
        <div className="space-y-2 text-sm">
          <p><strong>Required manifest fields:</strong> name, description, version, entry</p>
          <p><strong>Entry point:</strong> URL to your plugin&apos;s main JavaScript file</p>
          <p><strong>Security:</strong> Plugins run in sandboxed environments</p>
        </div>
      </div>
    </div>
  );
}
