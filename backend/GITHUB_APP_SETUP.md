# GitHub App Integration Setup

This guide explains how to set up the GitHub App integration for DevScope to automatically track your development activity.

## Overview

The GitHub App integration allows DevScope to:

- Automatically track commits and create activities
- Monitor pull request events
- Sync repository data
- Trigger AI analysis on new commits
- Provide real-time development insights

## Setting up the GitHub App

### 1. Create a GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Fill in the required information:

**Basic Information:**

- **GitHub App name**: `DevScope-[YourUsername]` (must be unique)
- **Description**: `DevScope developer analytics integration`
- **Homepage URL**: `https://your-devscope-domain.com`

**Identifying and authorizing users:**

- **Callback URL**: `https://your-backend-domain.com/api/v1/auth/github/callback`
- **Request user authorization (OAuth) during installation**: ✅
- **Webhook URL**: `https://your-backend-domain.com/api/v1/github/webhook`
- **Webhook secret**: Generate a secure random string (save this for later)

**Permissions:**

- **Repository permissions:**
  - Contents: Read
  - Metadata: Read
  - Pull requests: Read
  - Commit statuses: Read
- **Account permissions:**
  - Email addresses: Read

**Subscribe to events:**

- [x] Push
- [x] Pull request
- [x] Create
- [x] Delete

4. Click "Create GitHub App"

### 2. Generate and Download Private Key

1. In your newly created GitHub App settings
2. Scroll down to "Private keys"
3. Click "Generate a private key"
4. Download the `.pem` file and store it securely

### 3. Get App Details

Note down these important values from your GitHub App:

- **App ID** (shown at the top of the app settings)
- **Client ID** (in the OAuth credentials section)
- **Client Secret** (generate one if not already created)

### 4. Install the App

1. Go to the "Install App" tab in your GitHub App settings
2. Install it on your personal account or organization
3. Select repositories (can be all repos or specific ones)

## Backend Configuration

### Environment Variables

Add these variables to your backend `.env` file:

```bash
# GitHub App Configuration
GITHUB_APP_ID=your_app_id
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_PRIVATE_KEY_PATH=/path/to/your/private-key.pem
# Or embed the key directly (for deployment):
# GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"

# For user GitHub API access (optional)
GITHUB_TOKEN=your_personal_access_token
```

### Testing the Webhook

You can test the webhook integration:

1. **Local Development with ngrok:**

   ```bash
   # Install ngrok if you haven't already
   npm install -g ngrok

   # Expose your local backend
   ngrok http 8000

   # Update your GitHub App webhook URL to the ngrok URL
   # https://your-ngrok-url.ngrok.io/api/v1/github/webhook
   ```

2. **Check webhook status:**

   ```bash
   curl http://localhost:8000/api/v1/github/webhook/status
   ```

3. **Make a test commit** to trigger the webhook

4. **Check the logs** to see if events are being processed

## Webhook Events Handled

### Push Events

- Creates activities for each commit
- Estimates coding time based on file changes
- Triggers AI analysis (if configured)
- Links commits to projects automatically

### Pull Request Events

- Tracks PR creation, closing, and merging
- Creates appropriate activities with time estimates
- Links to repository projects

### Create/Delete Events

- Tracks repository and branch creation/deletion
- Creates planning activities for new repositories

## Security Considerations

1. **Webhook Secret**: Always use a strong, random webhook secret
2. **Private Key**: Store the GitHub App private key securely
3. **HTTPS**: Always use HTTPS for webhook URLs in production
4. **Rate Limiting**: GitHub has API rate limits - the integration handles this gracefully

## Troubleshooting

### Webhook Not Receiving Events

1. **Check the webhook URL** in your GitHub App settings
2. **Verify the webhook secret** matches your environment variable
3. **Check GitHub's webhook delivery logs** in the app settings
4. **Ensure your backend is accessible** from GitHub's servers

### Authentication Issues

1. **Verify all GitHub App credentials** are correct
2. **Check that the app is installed** on the relevant repositories
3. **Ensure the user's GitHub username** is set in DevScope

### Missing Activities

1. **Check that the pusher/author username** matches a DevScope user
2. **Verify the repository** is accessible by the GitHub App
3. **Check backend logs** for any error messages

## Production Deployment

### 1. Deploy Backend with GitHub Configuration

Ensure your production backend has:

- All GitHub environment variables set
- HTTPS endpoint accessible by GitHub
- Database configured to store activities

### 2. Update GitHub App Settings

- Set the production webhook URL
- Ensure callback URL points to production
- Test with a sample repository

### 3. User Onboarding

Users need to:

1. **Link their GitHub account** in DevScope settings
2. **Install the GitHub App** on their repositories
3. **Grant necessary permissions** during installation

## API Endpoints

The GitHub integration adds these API endpoints:

- `GET /api/v1/github/repos` - List user's repositories
- `GET /api/v1/github/commits/{repo_name}` - Get repository commits
- `GET /api/v1/github/stats` - Get GitHub statistics
- `POST /api/v1/github/sync-activity` - Manual activity sync
- `POST /api/v1/github/webhook` - Webhook endpoint (for GitHub)
- `GET /api/v1/github/webhook/status` - Webhook status check

## Advanced Features

### AI Analysis Integration

The webhook can trigger AI analysis for new commits:

1. **Set up the AI analyzer service** (see ai-engine documentation)
2. **Configure the trigger endpoint** in the webhook handler
3. **Commits will automatically** trigger AI classification

### Custom Event Handling

You can extend the webhook handler to support additional GitHub events:

1. **Add new event handlers** in `github_webhooks.py`
2. **Update the supported events list** in the webhook status endpoint
3. **Configure the new events** in your GitHub App settings

## Support

For issues with the GitHub integration:

1. Check the backend logs for error messages
2. Verify GitHub App configuration and permissions
3. Test webhook delivery in GitHub's interface
4. Consult the DevScope documentation for troubleshooting guides
