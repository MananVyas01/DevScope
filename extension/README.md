# DevScope VSCode Extension

A comprehensive developer productivity tracker that seamlessly integrates with your VS Code workflow to provide real-time insights into your coding sessions, productivity patterns, and development activity.

## Features

### 🔍 **Activity Tracking**

- **Automatic Session Detection**: Tracks coding sessions based on file changes and editor focus
- **File-Level Monitoring**: Records which files you work on and for how long
- **Language Detection**: Automatically identifies programming languages you're using
- **Keystroke Counting**: Measures coding activity intensity

### ⏱️ **Time Management**

- **Focus Time Tracking**: Distinguishes between active coding and idle time
- **Session Analytics**: Provides detailed breakdowns of your work sessions
- **Productivity Scoring**: Calculates productivity metrics based on focus vs. idle time
- **Real-time Monitoring**: Live updates in the sidebar as you code

### 🔗 **Git Integration**

- **Repository Detection**: Automatically identifies Git repositories and branches
- **Commit Correlation**: Links coding sessions to Git activity
- **Branch Tracking**: Shows which branch you're working on
- **Change Monitoring**: Tracks uncommitted changes in real-time

### 📊 **Productivity Dashboard**

- **Sidebar Panel**: Dedicated DevScope panel in VS Code's activity bar
- **Live Statistics**: Real-time display of current session metrics
- **Daily Summaries**: Overview of daily coding activity
- **Quick Actions**: One-click access to common DevScope features

### 🔄 **Backend Synchronization**

- **Automatic Sync**: Seamlessly syncs data with DevScope backend
- **Offline Support**: Continues tracking even when offline
- **Secure Communication**: Uses authenticated API calls for data sync
- **Error Handling**: Graceful handling of network issues and sync failures

## Installation

### From Source

1. Clone the DevScope repository
2. Navigate to the `extension` directory
3. Run `npm install` to install dependencies
4. Run `npm run compile` to build the extension
5. Press F5 to launch a new VS Code window with the extension loaded

## Configuration

### Basic Setup

1. Open VS Code Settings (Ctrl+, / Cmd+,)
2. Search for "DevScope"
3. Configure the following settings:

```json
{
  "devscope.apiUrl": "http://localhost:8000/api/v1",
  "devscope.enableTracking": true,
  "devscope.syncInterval": 300,
  "devscope.trackingInterval": 30
}
```

### Backend Connection

To sync your data with the DevScope backend:

```json
{
  "devscope.apiUrl": "https://your-devscope-backend.com/api/v1",
  "devscope.apiKey": "your-api-key-here",
  "devscope.userId": "your-user-id",
  "devscope.dashboardUrl": "https://your-devscope-frontend.com/dashboard"
}
```

## Available Commands

Access these commands via the Command Palette (Ctrl+Shift+P / Cmd+Shift+P):

- `DevScope: Show Productivity Summary` - Display detailed session summary
- `DevScope: Start Focus Session` - Begin a focused coding session
- `DevScope: Sync Now` - Manually sync data with backend
- `DevScope: Pause Tracking` - Temporarily pause activity tracking
- `DevScope: Resume Tracking` - Resume tracking after pause
- `DevScope: Open Dashboard` - Open DevScope web dashboard
- `DevScope: Open Settings` - Quick access to extension settings
- `DevScope: Reset Session` - Reset current tracking session

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes during development
npm run watch

# Test the extension
# Press F5 to open a new Extension Development Host window
```

## License

MIT
