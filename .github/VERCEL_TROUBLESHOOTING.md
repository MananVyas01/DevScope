# Vercel Deployment Troubleshooting

## 🚨 Current Issue: Missing VERCEL_TOKEN Secret

The deployment is failing with:

```
Error: Input required and not supplied: vercel-token
```

This indicates that the `VERCEL_TOKEN` secret is not configured in your GitHub repository.

## 🛠️ Solution: Configure GitHub Secrets

### Step 1: Get Your Vercel Token

1. Go to [Vercel Dashboard](https://vercel.com/account/tokens)
2. Click "Create Token"
3. Give it a name like "DevScope Deployment"
4. Copy the generated token

### Step 2: Get Project IDs

1. Go to your Vercel project settings
2. Copy the **Project ID** from the General tab
3. Copy the **Team ID** (this is your ORG_ID)

### Step 3: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

```
Name: VERCEL_TOKEN
Value: [Your Vercel token from step 1]

Name: PROJECT_ID
Value: [Your Vercel project ID]

Name: ORG_ID
Value: [Your Vercel team ID]

Name: NEXT_PUBLIC_SUPABASE_URL
Value: [Your Supabase project URL]

Name: NEXT_PUBLIC_SUPABASE_ANON_KEY
Value: [Your Supabase anon key]

Name: NEXT_PUBLIC_API_URL
Value: [Your backend API URL]
```

## 🔄 Alternative: Manual Deployment

If you want to deploy immediately without setting up the full CI/CD pipeline:

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel --prod
```

### Option 2: Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/new)
2. Import your GitHub repository
3. Set the root directory to `frontend`
4. Add environment variables in the dashboard
5. Deploy

## 🧪 Testing the Fix

After adding the secrets:

1. Push any change to the `frontend/` directory
2. Check the Actions tab in GitHub
3. Verify the deployment completes successfully

## 📋 Complete Secrets Checklist

- [ ] `VERCEL_TOKEN` - Vercel authentication token
- [ ] `PROJECT_ID` - Vercel project ID
- [ ] `ORG_ID` - Vercel organization/team ID
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key
- [ ] `NEXT_PUBLIC_API_URL` - Backend API URL

## 🔍 Debugging Steps

1. **Verify secrets exist**: Go to repository Settings → Secrets and variables → Actions
2. **Check secret names**: Ensure exact spelling (case-sensitive)
3. **Validate workflow**: Ensure the workflow file references correct secret names
4. **Test manually**: Try deploying via Vercel CLI to isolate the issue
