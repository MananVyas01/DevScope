# DevScope Backend - Railway Deployment

Railway deployment configuration for the DevScope FastAPI backend.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/DevScope-Backend)

## 📋 Deployment Steps

### 1. Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from this directory
cd backend/
railway link
railway up
```

### 2. Environment Variables

Set these environment variables in your Railway dashboard:

**Required:**

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- `JWT_SECRET` - Your Supabase JWT secret
- `SECRET_KEY` - Random secret key for API security
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Railway)

**Optional:**

- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_CLIENT_ID` - GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET` - GitHub OAuth app client secret
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `ENVIRONMENT` - Set to "production"
- `DEBUG` - Set to "false"
- `LOG_LEVEL` - Set to "INFO"

### 3. Database Setup

Railway will automatically provision a PostgreSQL database. The `DATABASE_URL` will be injected automatically.

### 4. Custom Domain (Optional)

1. Go to your Railway project dashboard
2. Click on your service
3. Go to Settings → Domains
4. Add your custom domain

## 🔧 Production Configuration

The app automatically configures itself for production when `ENVIRONMENT=production`:

- Debug mode disabled
- Production logging
- Security headers enabled
- Trusted host middleware
- Rate limiting active

## 📊 Monitoring

Health check endpoint: `https://your-app.railway.app/health`
API documentation: `https://your-app.railway.app/docs` (if DEBUG=true)

## 🔒 Security

- All endpoints require JWT authentication
- Rate limiting: 100 requests per minute per IP
- CORS configured for your frontend domains
- SQL injection protection via SQLAlchemy ORM
- Input validation via Pydantic schemas
