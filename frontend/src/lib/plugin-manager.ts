// Plugin system types and utilities

export interface PluginManifest {
  name: string;
  description: string;
  version: string;
  entry: string; // URL to plugin entry point
  author?: string;
  homepage?: string;
  repository?: string;
  permissions?: string[];
  category?: 'productivity' | 'analytics' | 'visualization' | 'utility' | 'other';
  tags?: string[];
  screenshots?: string[];
  icon?: string;
}

export interface InstalledPlugin {
  id: string;
  manifest: PluginManifest;
  installed_at: string;
  enabled: boolean;
  user_id: string;
}

export interface PluginRenderProps {
  user?: unknown;
  theme?: 'light' | 'dark';
  data?: unknown;
}

export class PluginManager {
  private installedPlugins: Map<string, InstalledPlugin> = new Map();
  private loadedPlugins: Map<string, unknown> = new Map();

  async validateManifest(manifest: unknown): Promise<PluginManifest> {
    // Basic validation
    if (!manifest || typeof manifest !== 'object') {
      throw new Error('Invalid manifest format');
    }
    
    const manifestObj = manifest as Record<string, unknown>;
    const required = ['name', 'description', 'version', 'entry'];
    for (const field of required) {
      if (!manifestObj[field]) {
        throw new Error(`Plugin manifest missing required field: ${field}`);
      }
    }

    // URL validation
    try {
      new URL(manifestObj.entry as string);
    } catch {
      throw new Error('Plugin entry must be a valid URL');
    }

    return manifestObj as unknown as PluginManifest;
  }

  async fetchManifestFromGitHub(repoUrl: string): Promise<PluginManifest> {
    try {
      // Convert GitHub repo URL to raw manifest URL
      const githubMatch = repoUrl.match(/github\.com\/([^/]+\/[^/]+)/);
      if (!githubMatch) {
        throw new Error('Invalid GitHub repository URL');
      }

      const repoPath = githubMatch[1];
      const manifestUrl = `https://raw.githubusercontent.com/${repoPath}/main/devscope-plugin.json`;
      
      const response = await fetch(manifestUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch manifest: ${response.statusText}`);
      }

      const manifest = await response.json();
      return await this.validateManifest(manifest);
    } catch (error) {
      throw new Error(`Failed to load plugin from GitHub: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async installPlugin(manifest: PluginManifest, userId: string): Promise<InstalledPlugin> {
    const plugin: InstalledPlugin = {
      id: `${manifest.name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`,
      manifest,
      installed_at: new Date().toISOString(),
      enabled: true,
      user_id: userId,
    };

    this.installedPlugins.set(plugin.id, plugin);
    
    // In a real app, save to database
    await this.saveToDatabase(plugin);
    
    return plugin;
  }

  async uninstallPlugin(pluginId: string): Promise<boolean> {
    if (this.installedPlugins.has(pluginId)) {
      this.installedPlugins.delete(pluginId);
      this.loadedPlugins.delete(pluginId);
      
      // In a real app, remove from database
      await this.removeFromDatabase(pluginId);
      return true;
    }
    return false;
  }

  async loadPlugin(pluginId: string): Promise<unknown> {
    const plugin = this.installedPlugins.get(pluginId);
    if (!plugin || !plugin.enabled) {
      return null;
    }

    if (this.loadedPlugins.has(pluginId)) {
      return this.loadedPlugins.get(pluginId);
    }

    try {
      // In a real implementation, this would load the plugin more securely
      const pluginModule = await this.dynamicImport(plugin.manifest.entry);
      this.loadedPlugins.set(pluginId, pluginModule);
      return pluginModule;
    } catch (error) {
      console.error(`Failed to load plugin ${pluginId}:`, error);
      return null;
    }
  }

  private async dynamicImport(entry: string): Promise<unknown> {
    // This is a simplified implementation
    // In production, you'd want more security measures
    try {
      const moduleResult = await import(/* webpackIgnore: true */ entry);
      return moduleResult;
    } catch {
      // Fallback: create script element (for non-ES modules)
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = entry;
        script.onload = () => {
          // Assume plugin registers itself globally
          const pluginName = entry.split('/').pop()?.replace('.js', '');
          resolve((window as unknown as Record<string, unknown>)[`DevScopePlugin_${pluginName}`]);
        };
        script.onerror = reject;
        document.head.appendChild(script);
      });
    }
  }

  private async saveToDatabase(plugin: InstalledPlugin): Promise<void> {
    // Mock implementation - in real app, use Supabase
    try {
      const stored = localStorage.getItem('devscope_plugins') || '[]';
      const plugins = JSON.parse(stored);
      plugins.push(plugin);
      localStorage.setItem('devscope_plugins', JSON.stringify(plugins));
    } catch (error) {
      console.error('Failed to save plugin to storage:', error);
    }
  }

  private async removeFromDatabase(pluginId: string): Promise<void> {
    // Mock implementation - in real app, use Supabase
    try {
      const stored = localStorage.getItem('devscope_plugins') || '[]';
      const plugins = JSON.parse(stored);
      const filtered = plugins.filter((p: InstalledPlugin) => p.id !== pluginId);
      localStorage.setItem('devscope_plugins', JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to remove plugin from storage:', error);
    }
  }

  async getInstalledPlugins(userId: string): Promise<InstalledPlugin[]> {
    // Mock implementation - load from localStorage
    try {
      const stored = localStorage.getItem('devscope_plugins') || '[]';
      const plugins = JSON.parse(stored);
      return plugins.filter((p: InstalledPlugin) => p.user_id === userId);
    } catch (error) {
      console.error('Failed to load plugins from storage:', error);
      return [];
    }
  }

  async togglePlugin(pluginId: string, enabled: boolean): Promise<boolean> {
    const plugin = this.installedPlugins.get(pluginId);
    if (plugin) {
      plugin.enabled = enabled;
      await this.saveToDatabase(plugin);
      
      if (!enabled) {
        this.loadedPlugins.delete(pluginId);
      }
      return true;
    }
    return false;
  }
}

// Global plugin manager instance
export const pluginManager = new PluginManager();
