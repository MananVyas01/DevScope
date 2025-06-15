'use client';

import { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';

interface PluginSandboxProps {
  pluginId: string;
  entry: string;
  props?: Record<string, unknown>;
  className?: string;
}

export function PluginSandbox({ pluginId, entry, props = {}, className = '' }: PluginSandboxProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!iframeRef.current) return;

    const iframe = iframeRef.current;
    
    // Create sandboxed HTML content for the plugin
    const sandboxContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>DevScope Plugin: ${pluginId}</title>
          <style>
            body {
              margin: 0;
              padding: 16px;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: transparent;
              color: inherit;
            }
            .plugin-container {
              width: 100%;
              height: 100%;
            }
            .error {
              color: #dc2626;
              padding: 16px;
              border: 1px solid #fecaca;
              border-radius: 8px;
              background: #fef2f2;
            }
            .loading {
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 32px;
              color: #6b7280;
            }
          </style>
        </head>
        <body>
          <div id="plugin-root" class="plugin-container">
            <div class="loading">Loading plugin...</div>
          </div>
          
          <script>
            // Plugin API for safe communication
            window.DevScopePlugin = {
              props: ${JSON.stringify(props)},
              render: function(element) {
                const root = document.getElementById('plugin-root');
                if (root && element) {
                  root.innerHTML = '';
                  if (typeof element === 'string') {
                    root.innerHTML = element;
                  } else {
                    root.appendChild(element);
                  }
                }
              },
              error: function(message) {
                const root = document.getElementById('plugin-root');
                if (root) {
                  root.innerHTML = '<div class="error">Plugin Error: ' + message + '</div>';
                }
              },
              ready: function() {
                window.parent.postMessage({
                  type: 'plugin-ready',
                  pluginId: '${pluginId}'
                }, '*');
              }
            };

            // Load the plugin script
            const script = document.createElement('script');
            script.onerror = function() {
              window.DevScopePlugin.error('Failed to load plugin script');
              window.parent.postMessage({
                type: 'plugin-error',
                pluginId: '${pluginId}',
                error: 'Failed to load plugin script'
              }, '*');
            };
            script.onload = function() {
              // Give plugin a moment to initialize
              setTimeout(() => {
                if (typeof window.initPlugin === 'function') {
                  try {
                    window.initPlugin();
                  } catch (e) {
                    window.DevScopePlugin.error(e.message);
                  }
                } else {
                  window.DevScopePlugin.error('Plugin must define initPlugin() function');
                }
              }, 100);
            };
            script.src = '${entry}';
            script.crossOrigin = 'anonymous';
            document.head.appendChild(script);
          </script>
        </body>
      </html>
    `;

    // Set up message listener for plugin communication
    const handleMessage = (event: MessageEvent) => {
      if (event.data.pluginId !== pluginId) return;
      
      switch (event.data.type) {
        case 'plugin-ready':
          setLoading(false);
          setError(null);
          break;
        case 'plugin-error':
          setLoading(false);
          setError(event.data.error || 'Plugin failed to load');
          break;
      }
    };

    window.addEventListener('message', handleMessage);

    // Load the sandboxed content
    const blob = new Blob([sandboxContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    iframe.src = url;

    return () => {
      window.removeEventListener('message', handleMessage);
      URL.revokeObjectURL(url);
    };
  }, [pluginId, entry, props]);

  return (
    <div className={`relative ${className}`}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 z-10">
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading plugin...</span>
          </div>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50 dark:bg-red-900/20 z-10">
          <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}
      
      <iframe
        ref={iframeRef}
        className="w-full h-full border-0"
        sandbox="allow-scripts allow-same-origin"
        title={`Plugin: ${pluginId}`}
      />
    </div>
  );
}

export default PluginSandbox;
