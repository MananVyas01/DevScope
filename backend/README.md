# DevScope Backend API 🚀

A comprehensive FastAPI backend for the DevScope developer analytics platform, providing JWT authentication, advanced analytics, GitHub integration, focus timer functionality, and mood tracking.

## 🏗️ Architecture

Built with **FastAPI** and **PostgreSQL**, this backend provides:

- 🔐 **JWT Authentication** via Supabase
- 📊 **Advanced Analytics** with trend analysis
- 🐙 **GitHub Integration** with activity sync
- ⏱️ **Focus Timer** with session management
- 😊 **Mood Tracking** with correlation analysis
- 🛡️ **Security & Rate Limiting**
- 🔍 **Comprehensive Logging**

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (or SQLite for development)
- Supabase account (optional for local development)

### Local Development

1. **Clone and Navigate**

   ```bash
   git clone <repository-url>
   cd backend/
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Server**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── api/v1/                # API version 1
│   │   ├── api.py            # Router aggregation
│   │   └── endpoints/        # Endpoint modules
│   │       ├── auth.py       # Authentication
│   │       ├── users.py      # User management
│   │       ├── analytics.py  # Analytics & stats
│   │       ├── github.py     # GitHub integration
│   │       ├── timer.py      # Focus timer
│   │       └── mood.py       # Mood tracking
│   ├── auth/                  # Authentication logic
│   │   ├── dependencies.py   # Auth dependencies
│   │   └── supabase_auth.py  # Supabase integration
│   ├── middleware/           # Custom middleware
│   │   ├── auth.py          # Auth middleware
│   │   └── logging.py       # Request logging
│   ├── models/              # Database models
│   │   ├── database.py      # DB configuration
│   │   └── models.py        # SQLAlchemy models
│   └── schemas/             # Pydantic schemas
│       └── schemas.py       # Request/response models
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── Dockerfile              # Container configuration
├── railway.json            # Railway deployment config
└── README.md               # This file
```

## 🔧 API Endpoints

### 🔐 Authentication (`/api/v1/auth`)

- `POST /login` - User authentication
- `POST /refresh` - Token refresh
- `POST /verify` - Token verification
- `POST /logout` - User logout
- `GET /me` - Current user profile
- `GET /github/callback` - GitHub OAuth callback

### 👤 Users (`/api/v1/users`)

- `GET /me` - Get user profile
- `PUT /me` - Update profile
- `DELETE /me` - Delete account
- `GET /me/stats` - User statistics

### 📊 Analytics (`/api/v1/analytics`)

- `GET /dashboard` - Dashboard summary
- `GET /daily` - Daily analytics
- `GET /productivity-trends` - Productivity over time
- `GET /project-breakdown` - Project time allocation

### 🐙 GitHub (`/api/v1/github`)

- `GET /repos` - User repositories
- `GET /commits/{repo}` - Repository commits
- `GET /stats` - GitHub statistics
- `POST /sync-activity` - Sync commits to activities

### ⏱️ Focus Timer (`/api/v1/timer`)

- `POST /start` - Start timer session
- `GET /session/{id}` - Session status
- `POST /session/{id}/pause` - Pause session
- `POST /session/{id}/resume` - Resume session
- `POST /session/{id}/complete` - Complete session
- `GET /active` - Active sessions
- `GET /history` - Session history

### 😊 Mood Tracking (`/api/v1/mood`)

- `POST /` - Create mood entry
- `GET /` - List mood entries
- `GET /{id}` - Get mood entry
- `PUT /{id}` - Update mood entry
- `DELETE /{id}` - Delete mood entry
- `GET /analytics/trends` - Mood trends
- `GET /analytics/correlations` - Mood correlations
- `GET /quick-check` - Quick mood prompt

## 🗄️ Database Models

### Core Models

- **User** - User profiles with GitHub integration
- **Activity** - Tracked activities with duration and categorization
- **Mood** - Mood entries with multiple metrics
- **Project** - Project management with GitHub linking
- **ProjectStats** - Aggregated statistics for performance

### Relationships

- Users have many Activities, Moods, Projects
- Projects have many Activities and ProjectStats
- Full referential integrity with cascading deletes

## 🛡️ Security Features

- **JWT Authentication** with Supabase integration
- **Rate Limiting** (100 requests/minute per IP)
- **CORS Protection** with configurable origins
- **Input Validation** via Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM
- **Secure Headers** in production mode

## 🔧 Configuration

### Environment Variables

**Required:**

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
JWT_SECRET=your_jwt_secret
SECRET_KEY=your_api_secret_key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Optional:**

```bash
GITHUB_TOKEN=your_github_token
GITHUB_CLIENT_ID=your_github_oauth_id
GITHUB_CLIENT_SECRET=your_github_oauth_secret
OPENAI_API_KEY=your_openai_key
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## 🚀 Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up
```

### Docker

```bash
# Build image
docker build -t devscope-backend .

# Run container
docker run -p 8000:8000 --env-file .env devscope-backend
```

### Manual Deployment

1. Set environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Start server: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🧪 Testing

### API Testing

- **Swagger UI**: Built-in at `/docs`
- **Postman Collection**: `DevScope_API.postman_collection.json`
- **Health Checks**: `/health` and `/api/v1/health`

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📊 Monitoring

### Health Checks

- **Basic**: `GET /health`
- **API**: `GET /api/v1/health`
- **Database**: Included in health checks

### Logging

- **Structured Logging** with request IDs
- **Performance Metrics** with response times
- **Error Tracking** with stack traces
- **Request/Response Logging** for debugging

## 🔄 Development Workflow

1. **Feature Development**

   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

2. **Testing**

   ```bash
   pytest
   # Test API endpoints
   # Verify functionality
   ```

3. **Deployment**
   ```bash
   git checkout main
   git merge feature/new-feature
   git push origin main
   # Auto-deploy via Railway/CI
   ```

## 📚 API Documentation

- **Interactive Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **OpenAPI Schema**: `/openapi.json`
- **Postman Collection**: Import `DevScope_API.postman_collection.json`

## 🆘 Support

- **Documentation**: See `/docs` endpoint
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**DevScope Backend - Empowering Developer Analytics** 🚀

````

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
````

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Run the development server:

```bash
npm run dev
```

## API Documentation

Once running, visit:

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```
