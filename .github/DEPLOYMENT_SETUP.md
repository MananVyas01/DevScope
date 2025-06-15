# Deployment Setup Guide

This document explains how to set up the required secrets and configurations for deploying the DevScope application.

## Required GitHub Secrets

To enable automatic deployment, you need to configure the following secrets in your GitHub repository settings:

### 1. Navigate to Repository Settings

- Go to your GitHub repository
- Click on **Settings** tab
- Click on **Secrets and variables** > **Actions**

### 2. Add Required Secrets

#### Vercel Deployment Secrets

```
VERCEL_TOKEN - Your Vercel authentication token
ORG_ID - Your Vercel organization ID
PROJECT_ID - Your Vercel project ID
```

#### Backend API Configuration

```
NEXT_PUBLIC_API_URL - Your backend API URL (e.g., https://your-backend.railway.app)
```

#### Supabase Configuration

```
NEXT_PUBLIC_SUPABASE_URL - Your Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY - Your Supabase anonymous key
```

## How to Get These Values

### Vercel Secrets

1. **VERCEL_TOKEN**:
   - Go to [Vercel Dashboard](https://vercel.com/account/tokens)
   - Create a new token with appropriate scopes
2. **ORG_ID**:
   - Go to your Vercel team settings
   - Copy the Team ID (this is your ORG_ID)
3. **PROJECT_ID**:
   - Go to your Vercel project settings
   - Copy the Project ID from the General tab

### Supabase Secrets

1. **NEXT_PUBLIC_SUPABASE_URL**:
   - Go to your [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project
   - Go to Settings > API
   - Copy the Project URL
2. **NEXT_PUBLIC_SUPABASE_ANON_KEY**:
   - In the same API settings page
   - Copy the `anon` `public` key

### Backend API URL

- **NEXT_PUBLIC_API_URL**: This should be the URL where your backend is deployed (e.g., Railway, Heroku, etc.)

## Workflow Triggers

The deployment workflow is triggered when:

- Code is pushed to the `main` branch
- Changes are made to files in the `frontend/` directory

## Troubleshooting

### Common Errors

1. **"Input required and not supplied: vercel-token"**

   - This means the `VERCEL_TOKEN` secret is missing
   - Double-check that the secret is added with the exact name `VERCEL_TOKEN`

2. **Build failures**

   - Check that all environment variables are properly set
   - Verify that the Supabase URL and keys are valid

3. **Deployment failures**
   - Ensure the Vercel project exists and the PROJECT_ID is correct
   - Verify that the VERCEL_TOKEN has the necessary permissions

## Testing the Setup

After adding all secrets, push a small change to the frontend to trigger the deployment workflow and verify everything works correctly.
