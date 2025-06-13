# Deployment Guide - DevScope Frontend

## 🚀 Vercel Deployment

The frontend is ready for deployment on Vercel with the following setup:

### Build Configuration

- **Framework**: Next.js 15
- **Node Version**: 18+
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

### Environment Variables Required

Set these in your Vercel dashboard:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Deployment Steps

1. **Connect GitHub Repository**

   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import your GitHub repository
   - Select the `frontend` folder as the root directory

2. **Configure Build Settings**

   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Set Environment Variables**

   - Add your Supabase URL and anon key
   - These should match your Supabase project settings

4. **Deploy**
   - Vercel will automatically deploy on every push to main
   - The app will be available at `https://your-app.vercel.app`

### Features Deployed

✅ **Landing Page** with GitHub OAuth
✅ **Responsive Dashboard** with analytics
✅ **Dark/Light Mode** theme switching
✅ **Navigation** to all sections
✅ **Chart.js Integration** with mock data

### Post-Deployment Setup

1. Update your Supabase Auth settings:

   - Add your Vercel domain to allowed origins
   - Update redirect URLs to include your production URL

2. Test the OAuth flow:
   - Visit your deployed app
   - Try signing in with GitHub
   - Verify dashboard access

## 📱 Mobile Responsive

The app is fully responsive and works on:

- 📱 Mobile devices (iOS/Android)
- 📱 Tablets
- 💻 Desktop browsers
- 🌙 Dark mode support

## 🔄 Automatic Deployments

Every push to the `main` branch will trigger:

- ✅ Automatic build
- ✅ TypeScript compilation (errors ignored for MVP)
- ✅ Production deployment
- ✅ Edge distribution via Vercel CDN
