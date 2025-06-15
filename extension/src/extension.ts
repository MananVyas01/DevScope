import * as vscode from 'vscode';
import * as path from 'path';
import axios, { AxiosResponse } from 'axios';

// Declare global timer functions to avoid ESLint errors
// eslint-disable-next-line no-unused-vars
declare const setInterval: (_callback: () => void, _ms: number) => number;
// eslint-disable-next-line no-unused-vars
declare const clearInterval: (_id: number) => void;

interface ActivitySession {
  startTime: Date;
  endTime?: Date;
  files: Set<string>;
  keystrokes: number;
  focusTime: number;
  idleTime: number;
  language?: string;
  project?: string;
  gitRepo?: string;
  gitBranch?: string;
}

interface ProductivityData {
  totalTime: number;
  focusTime: number;
  filesEdited: number;
  languages: string[];
  productivity: number;
  gitActivity?: GitActivity;
}

interface GitActivity {
  repository: string;
  branch: string;
  lastCommit?: string;
  uncommittedChanges: number;
}

interface BackendConfig {
  apiUrl: string;
  apiKey?: string;
  userId?: string;
}

interface SyncPayload {
  sessionId: string;
  startTime: string;
  endTime: string;
  filesEdited: string[];
  keystrokes: number;
  focusTime: number;
  idleTime: number;
  language?: string;
  project?: string;
  gitRepo?: string;
  gitBranch?: string;
  metadata?: Record<string, unknown>;
}

class DevScopeTracker {
  private currentSession: ActivitySession | null = null;
  public isTracking: boolean = true;
  private lastActivity: Date = new Date();
  private idleThreshold: number = 30000; // 30 seconds
  private syncTimer: number | null = null;
  private activityTimer: number | null = null;
  private outputChannel: vscode.OutputChannel;
  public sidebarProvider: DevScopeSidebarProvider;
  private sessionId: string = '';
  private gitExtension: vscode.Extension<any> | undefined; // eslint-disable-line @typescript-eslint/no-explicit-any

  constructor(private context: vscode.ExtensionContext) {
    this.outputChannel = vscode.window.createOutputChannel('DevScope');
    this.sidebarProvider = new DevScopeSidebarProvider(context, this);
    this.sessionId = this.generateSessionId();
    this.initializeGitExtension();
    this.setupEventListeners();
    this.startTracking();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async initializeGitExtension() {
    try {
      this.gitExtension = vscode.extensions.getExtension('vscode.git')?.exports;
      if (this.gitExtension) {
        this.outputChannel.appendLine('Git extension initialized');
      }
    } catch (error) {
      this.outputChannel.appendLine(
        `Failed to initialize Git extension: ${error}`
      );
    }
  }

  private async getGitInfo(): Promise<GitActivity | undefined> {
    try {
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders || !this.gitExtension) return undefined;

      const api = this.gitExtension?.exports?.getAPI(1);
      if (!api) return undefined;

      const repo = api.repositories[0];
      if (!repo) return undefined;

      // Get repository info
      const remoteUrl = repo.state.remotes[0]?.fetchUrl || '';
      const branch = repo.state.HEAD?.name || 'main';

      // Extract repository name from URL
      const repoMatch = remoteUrl.match(/github\.com[/:](.+?)(?:\.git)?$/);
      const repository = repoMatch
        ? repoMatch[1]
        : path.basename(workspaceFolders[0].uri.fsPath);

      // Count uncommitted changes
      const uncommittedChanges =
        repo.state.workingTreeChanges.length + repo.state.indexChanges.length;

      return {
        repository,
        branch,
        lastCommit: repo.state.HEAD?.commit,
        uncommittedChanges,
      };
    } catch (error) {
      this.outputChannel.appendLine(`Error getting Git info: ${error}`);
      return undefined;
    }
  }

  private setupEventListeners() {
    // File change tracking
    vscode.workspace.onDidChangeTextDocument(event => {
      if (this.isTracking && event.document.uri.scheme === 'file') {
        this.recordActivity(event.document);
      }
    });

    // File open/close tracking
    vscode.window.onDidChangeActiveTextEditor(editor => {
      if (this.isTracking && editor) {
        this.recordActivity(editor.document);
      }
    });

    // Focus/blur tracking
    vscode.window.onDidChangeWindowState(state => {
      if (state.focused) {
        this.recordActivity();
      }
    });
  }

  private recordActivity(document?: vscode.TextDocument) {
    this.lastActivity = new Date();

    if (!this.currentSession) {
      this.startSession();
    }

    if (this.currentSession && document) {
      this.currentSession.files.add(document.fileName);
      this.currentSession.keystrokes++;

      // Update language if available
      if (document.languageId) {
        this.currentSession.language = document.languageId;
      }
    }

    this.sidebarProvider.refresh();
  }

  public async startSession() {
    const gitInfo = await this.getGitInfo();

    this.currentSession = {
      startTime: new Date(),
      files: new Set<string>(),
      keystrokes: 0,
      focusTime: 0,
      idleTime: 0,
      project: this.getCurrentProject(),
      gitRepo: gitInfo?.repository,
      gitBranch: gitInfo?.branch,
    };

    this.outputChannel.appendLine(
      `Started new session at ${this.currentSession.startTime.toLocaleTimeString()}`
    );
    this.outputChannel.appendLine(`Project: ${this.currentSession.project}`);
    if (gitInfo) {
      this.outputChannel.appendLine(
        `Git: ${gitInfo.repository}@${gitInfo.branch} (${gitInfo.uncommittedChanges} changes)`
      );
    }
  }

  private getCurrentProject(): string {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
      return path.basename(workspaceFolders[0].uri.fsPath);
    }
    return 'Unknown Project';
  }

  private startTracking() {
    // Check for idle state every 5 seconds
    this.activityTimer = setInterval(() => {
      const now = new Date();
      const timeSinceActivity = now.getTime() - this.lastActivity.getTime();

      if (timeSinceActivity > this.idleThreshold) {
        // User is idle
        if (this.currentSession) {
          this.currentSession.idleTime += 5;
        }
      } else {
        // User is active
        if (this.currentSession) {
          this.currentSession.focusTime += 5;
        }
      }
    }, 5000);

    // Sync data every 5 minutes
    const syncInterval =
      vscode.workspace.getConfiguration('devscope').get('syncInterval', 300) *
      1000;
    this.syncTimer = setInterval(() => {
      this.syncData();
    }, syncInterval);
  }

  public async syncData() {
    if (!this.currentSession) return;

    try {
      const config = this.getBackendConfig();
      if (!config.apiUrl) {
        this.outputChannel.appendLine('API URL not configured. Skipping sync.');
        return;
      }

      const sessionData = await this.getSessionData();
      if (!sessionData) return;

      this.outputChannel.appendLine('Syncing session data to backend...');

      // Make HTTP request to backend
      const response: AxiosResponse = await axios.post(
        `${config.apiUrl}/vscode/activity`,
        sessionData,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(config.apiKey && { Authorization: `Bearer ${config.apiKey}` }),
            'User-Agent': 'DevScope-VSCode-Extension/1.0.0',
          },
          timeout: 10000,
        }
      );

      if (response.status === 200 || response.status === 201) {
        this.outputChannel.appendLine('✅ Session data synced successfully');

        // Reset session after successful sync
        this.startSession();
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error: unknown) {
      let errorMessage = 'Unknown error';

      const errorObj = error as {
        code?: string;
        response?: {
          status: number;
          data?: { message: string };
          statusText: string;
        };
        message?: string;
      };

      if (errorObj.code === 'ECONNREFUSED') {
        errorMessage = 'Connection refused - is the DevScope backend running?';
      } else if (errorObj.response) {
        errorMessage = `HTTP ${errorObj.response.status}: ${errorObj.response.data?.message || errorObj.response.statusText}`;
      } else if (errorObj.message) {
        errorMessage = errorObj.message;
      }

      this.outputChannel.appendLine(`❌ Sync failed: ${errorMessage}`);

      // Show user-friendly error message for common issues
      if (error.code === 'ECONNREFUSED') {
        vscode.window
          .showWarningMessage(
            'DevScope backend is not reachable. Please check your configuration and ensure the backend is running.',
            'Open Settings'
          )
          .then(selection => {
            if (selection === 'Open Settings') {
              vscode.commands.executeCommand(
                'workbench.action.openSettings',
                'devscope'
              );
            }
          });
      }
    }
  }

  private getBackendConfig(): BackendConfig {
    const config = vscode.workspace.getConfiguration('devscope');
    return {
      apiUrl: config.get('apiUrl', 'http://localhost:8000/api/v1'),
      apiKey: config.get('apiKey'),
      userId: config.get('userId'),
    };
  }

  private async getSessionData(): Promise<SyncPayload | null> {
    if (!this.currentSession) return null;

    const gitInfo = await this.getGitInfo();
    const now = new Date();

    return {
      sessionId: this.sessionId,
      startTime: this.currentSession.startTime.toISOString(),
      endTime: now.toISOString(),
      filesEdited: Array.from(this.currentSession.files),
      keystrokes: this.currentSession.keystrokes,
      focusTime: this.currentSession.focusTime,
      idleTime: this.currentSession.idleTime,
      language: this.currentSession.language,
      project: this.currentSession.project,
      gitRepo: this.currentSession.gitRepo,
      gitBranch: this.currentSession.gitBranch,
      metadata: {
        gitInfo,
        vscodeVersion: vscode.version,
        extensionVersion: '1.0.0',
        workspaceCount: vscode.workspace.workspaceFolders?.length || 0,
      },
    };
  }

  public async getProductivitySummary(): Promise<ProductivityData> {
    const gitInfo = await this.getGitInfo();

    if (!this.currentSession) {
      return {
        totalTime: 0,
        focusTime: 0,
        filesEdited: 0,
        languages: [],
        productivity: 0,
        gitActivity: gitInfo,
      };
    }

    const totalTime =
      this.currentSession.focusTime + this.currentSession.idleTime;
    const productivity =
      totalTime > 0 ? (this.currentSession.focusTime / totalTime) * 100 : 0;

    return {
      totalTime: totalTime,
      focusTime: this.currentSession.focusTime,
      filesEdited: this.currentSession.files.size,
      languages: this.currentSession.language
        ? [this.currentSession.language]
        : [],
      productivity: Math.round(productivity),
      gitActivity: gitInfo,
    };
  }

  public pauseTracking() {
    this.isTracking = false;
    this.outputChannel.appendLine('Tracking paused');
  }

  public resumeTracking() {
    this.isTracking = true;
    this.outputChannel.appendLine('Tracking resumed');
  }

  public dispose() {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }
    if (this.activityTimer) {
      clearInterval(this.activityTimer);
    }
    this.outputChannel.dispose();
  }
}

class DevScopeSidebarProvider implements vscode.TreeDataProvider<SidebarItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<
    SidebarItem | undefined | null | void
  > = new vscode.EventEmitter<SidebarItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<
    SidebarItem | undefined | null | void
  > = this._onDidChangeTreeData.event;

  constructor(
    // eslint-disable-next-line no-unused-vars
    private _context: vscode.ExtensionContext,
    // eslint-disable-next-line no-unused-vars
    private _tracker: DevScopeTracker
  ) {
    // Constructor parameters stored as private properties
  }

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: SidebarItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: SidebarItem): Promise<SidebarItem[]> {
    if (!element) {
      // Root items
      return [
        new SidebarItem(
          "📊 Today's Summary",
          vscode.TreeItemCollapsibleState.Expanded
        ),
        new SidebarItem(
          '⏱️ Current Session',
          vscode.TreeItemCollapsibleState.Expanded
        ),
        new SidebarItem(
          '🔗 Git Status',
          vscode.TreeItemCollapsibleState.Expanded
        ),
        new SidebarItem(
          '🎯 Quick Actions',
          vscode.TreeItemCollapsibleState.Collapsed
        ),
      ];
    } else {
      // Child items based on parent
      if (element.label === "📊 Today's Summary") {
        const summary = await this._tracker.getProductivitySummary();
        return [
          new SidebarItem(`Focus Time: ${Math.round(summary.focusTime / 60)}m`),
          new SidebarItem(`Files Edited: ${summary.filesEdited}`),
          new SidebarItem(`Productivity: ${summary.productivity}%`),
          new SidebarItem(
            `Languages: ${summary.languages.join(', ') || 'None'}`
          ),
        ];
      } else if (element.label === '⏱️ Current Session') {
        const summary = await this._tracker.getProductivitySummary();
        const sessionTime = Math.round(summary.totalTime / 60);
        return [
          new SidebarItem(`Session: ${sessionTime}m`),
          new SidebarItem(`Files: ${summary.filesEdited}`),
          new SidebarItem(
            `Status: ${this._tracker.isTracking ? 'Active' : 'Paused'}`
          ),
        ];
      } else if (element.label === '🔗 Git Status') {
        const summary = await this._tracker.getProductivitySummary();
        const git = summary.gitActivity;
        if (git) {
          return [
            new SidebarItem(`Repo: ${git.repository}`),
            new SidebarItem(`Branch: ${git.branch}`),
            new SidebarItem(`Changes: ${git.uncommittedChanges || 0}`),
          ];
        } else {
          return [new SidebarItem('No Git repository detected')];
        }
      } else if (element.label === '🎯 Quick Actions') {
        return [
          new SidebarItem(
            'Start Focus Session',
            vscode.TreeItemCollapsibleState.None,
            'devscope.startFocusSession'
          ),
          new SidebarItem(
            'Sync Now',
            vscode.TreeItemCollapsibleState.None,
            'devscope.syncNow'
          ),
          new SidebarItem(
            'Pause Tracking',
            vscode.TreeItemCollapsibleState.None,
            'devscope.pauseTracking'
          ),
          new SidebarItem(
            'Open Dashboard',
            vscode.TreeItemCollapsibleState.None,
            'devscope.openDashboard'
          ),
          new SidebarItem(
            'Settings',
            vscode.TreeItemCollapsibleState.None,
            'devscope.openSettings'
          ),
        ];
      }
      return [];
    }
  }
}

class SidebarItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState?: vscode.TreeItemCollapsibleState,
    commandId?: string
  ) {
    super(label, collapsibleState);

    if (commandId) {
      this.command = {
        command: commandId,
        title: label,
      };
    }
  }
}

let tracker: DevScopeTracker;

export function activate(context: vscode.ExtensionContext) {
  // Initialize tracker
  tracker = new DevScopeTracker(context);

  // Register sidebar provider
  vscode.window.registerTreeDataProvider(
    'devscope-sidebar',
    tracker.sidebarProvider
  );

  // Register commands
  const commands = [
    vscode.commands.registerCommand(
      'devscope.showProductivitySummary',
      async () => {
        const summary = await tracker.getProductivitySummary();
        const git = summary.gitActivity;
        const gitInfo = git
          ? `\n\n🔗 Git: ${git.repository}@${git.branch}` +
            (git.uncommittedChanges
              ? ` (${git.uncommittedChanges} changes)`
              : '')
          : '';

        const message = `📊 Productivity Summary
      
Focus Time: ${Math.round(summary.focusTime / 60)}m
Files Edited: ${summary.filesEdited}
Productivity: ${summary.productivity}%
Languages: ${summary.languages.join(', ') || 'None'}${gitInfo}`;

        vscode.window.showInformationMessage(message);
      }
    ),

    vscode.commands.registerCommand('devscope.startFocusSession', () => {
      vscode.window.showInformationMessage(
        '🎯 Focus session started! Stay productive!'
      );
      // TODO: Integrate with Pomodoro timer
    }),

    vscode.commands.registerCommand('devscope.syncNow', async () => {
      vscode.window.showInformationMessage('🔄 Syncing data...');
      await tracker.syncData();
      tracker.sidebarProvider.refresh();
    }),

    vscode.commands.registerCommand('devscope.pauseTracking', () => {
      tracker.pauseTracking();
      tracker.sidebarProvider.refresh();
      vscode.window.showInformationMessage('⏸️ Tracking paused');
    }),

    vscode.commands.registerCommand('devscope.resumeTracking', () => {
      tracker.resumeTracking();
      tracker.sidebarProvider.refresh();
      vscode.window.showInformationMessage('▶️ Tracking resumed');
    }),

    vscode.commands.registerCommand('devscope.openDashboard', () => {
      const config = vscode.workspace.getConfiguration('devscope');
      const dashboardUrl = config.get(
        'dashboardUrl',
        'http://localhost:3000/dashboard'
      );
      vscode.env.openExternal(vscode.Uri.parse(dashboardUrl));
    }),

    vscode.commands.registerCommand('devscope.openSettings', () => {
      vscode.commands.executeCommand(
        'workbench.action.openSettings',
        'devscope'
      );
    }),

    vscode.commands.registerCommand('devscope.resetSession', async () => {
      const result = await vscode.window.showWarningMessage(
        'Are you sure you want to reset the current session? This will clear all unsaved tracking data.',
        'Reset',
        'Cancel'
      );

      if (result === 'Reset') {
        await tracker.startSession();
        tracker.sidebarProvider.refresh();
        vscode.window.showInformationMessage('🔄 Session reset');
      }
    }),
  ];

  commands.forEach(command => context.subscriptions.push(command));
  context.subscriptions.push(tracker);

  // Show welcome message
  vscode.window.showInformationMessage(
    '🚀 DevScope extension activated! Tracking your productivity...'
  );
}

export function deactivate() {
  if (tracker) {
    tracker.dispose();
  }
}
