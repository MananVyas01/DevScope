# 🎯 DevScope - Developer Productivity, Reimagined

[![Development Stage](https://img.shields.io/badge/Status-Stage%205%20Complete-success?style=for-the-badge)](#-current-development-stage)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](#)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Tauri](https://img.shields.io/badge/Tauri-24C8D8?style=for-the-badge&logo=tauri&logoColor=white)](#)

> **An all-in-one productivity tracker for developers.** Track coding activity, analyze focus patterns, visualize GitHub contributions, and get AI-powered workflow insights — locally, privately, and beautifully.

## 🚀 **Project Overview**

DevScope is a comprehensive **full-stack monorepo** designed to revolutionize developer productivity tracking. Built with modern technologies and a focus on **privacy-first, offline-capable** architecture.

### **🎯 Key Features**

- **🕒 Smart Focus Timer** - Pomodoro technique with real-time activity monitoring
- **📊 Mood & Productivity Tracking** - Comprehensive analytics with correlation insights
- **🔄 Offline-First Architecture** - Works seamlessly without internet connection
- **📱 Multi-Platform Support** - Web app, desktop app, and VS Code extension
- **🔐 Privacy-Focused** - Local data storage with optional cloud sync
- **🤖 AI-Powered Insights** - Machine learning for productivity optimization
- **🐙 GitHub Integration** - Automatic webhook processing for commit analysis
- **🔌 VSCode Extension** - Real-time productivity tracking in your editor

---

## 🏗️ **Architecture & Tech Stack**

### **Frontend** (Production Ready ✅)

- **Framework**: Next.js 15 + React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Supabase Auth
- **State Management**: React Hooks + Context
- **Charts**: Chart.js + React-ChartJS-2

### **Backend** (Production Ready ✅)

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: JWT + Supabase integration
- **API Documentation**: OpenAPI/Swagger
- **Deployment**: Railway + Docker

### **Desktop App** (In Development 🚧)

- **Framework**: Tauri + React
- **Language**: Rust + TypeScript
- **Platform**: Cross-platform (Windows, macOS, Linux)

### **VS Code Extension** (Production Ready ✅)

- **Language**: TypeScript
- **Integration**: VS Code API
- **Features**: Activity tracking, productivity sidebar, Git integration
- **Backend Sync**: Real-time session synchronization

### **AI Engine** (Production Ready ✅)

- **Language**: Python
- **ML Libraries**: OpenAI GPT integration
- **Features**: Commit analysis, productivity insights, activity classification

---

## 🎯 **Current Development Stage**

### **Stage 5: GitHub & VSCode Integration** ✅ **COMPLETE**

**Delivered Features:**

#### 🔌 **VSCode Extension**

- ✅ **Activity Tracking** - Real-time file monitoring and session detection
- ✅ **Productivity Sidebar** - Live productivity metrics and session stats
- ✅ **Git Integration** - Repository context and branch tracking
- ✅ **Backend Sync** - Automatic synchronization with DevScope backend
- ✅ **Idle Detection** - Smart idle time tracking and session management
- ✅ **Error Handling** - Robust offline support and error recovery

#### 🐙 **GitHub App Integration**

- ✅ **Webhook Processing** - Automated push, PR, and review event handling
- ✅ **AI Commit Analysis** - GPT-powered commit message and diff analysis
- ✅ **Security** - GitHub signature verification and secure webhook handling
- ✅ **Rate Limiting** - Intelligent request management and retry logic
- ✅ **Database Integration** - Full activity storage and retrieval

#### 🚀 **Backend Enhancements**

- ✅ **VSCode API Endpoints** - Complete `/vscode/*` API suite
- ✅ **GitHub Event Processing** - Enhanced `/github-events` handling
- ✅ **Authentication Improvements** - Dev/prod mode support
- ✅ **Error Handling** - Comprehensive logging and monitoring

### **Previous Stages:**

### **Stage 3: Smart Focus Timer + Mood Tracker** ✅ **COMPLETE**

**Delivered Features:**

- ✅ **Pomodoro Timer** with 25/5 minute focus/break cycles
- ✅ **Real-time Activity Monitoring** (keyboard/mouse tracking)
- ✅ **Idle Detection** with 30-second threshold and notifications
- ✅ **Comprehensive Mood Tracking** with post-session analytics
- ✅ **Offline Support** with localStorage and automatic sync
- ✅ **Session Statistics** with real-time updates
- ✅ **Production APIs** with full authentication and security

**Technical Achievements:**

- Complete **offline-first architecture** with sync capabilities
- **Real-time activity monitoring** with efficient event handling
- **Comprehensive analytics engine** with mood-productivity correlations
- **Production-ready security** with JWT, rate limiting, and CORS
- **Type-safe development** with TypeScript throughout

---

## 📂 **Project Structure**

```
DevScope/
├── 🌐 frontend/          # Next.js web application (✅ Complete)
│   ├── src/app/          # App router with dashboard
│   ├── src/components/   # Reusable UI components
│   ├── src/lib/          # API client & utilities
│   └── src/hooks/        # Custom React hooks
│
├── ⚡ backend/           # FastAPI server (✅ Complete)
│   ├── app/api/          # API endpoints & routing
│   ├── app/auth/         # Authentication logic
│   ├── app/models/       # Database models
│   └── app/schemas/      # Pydantic schemas
│
├── 🖥️ desktop/          # Tauri desktop app (🚧 In Progress)
│   ├── src/              # React frontend
│   └── src-tauri/        # Rust backend
│
├── 🔌 extension/         # VS Code extension (✅ Complete)
│   ├── src/              # TypeScript extension code
│   ├── package.json      # Extension manifest
│   └── README.md         # Extension documentation
│
└── 🤖 ai-engine/         # ML analytics (✅ Complete)
    ├── analyzer.py       # AI commit analysis
    ├── git_parser.py     # Git repository processing
    └── main.py           # Analysis pipeline
```

---

## 🚀 **Getting Started**

### **Prerequisites**

- Node.js 18+
- Python 3.12+
- PostgreSQL (or SQLite for development)
- Supabase account (for authentication)

### **Quick Start**

1. **Clone the repository**

   ```bash
   git clone https://github.com/MananVyas01/DevScope.git
   cd DevScope
   ```

2. **Install dependencies**

   ```bash
   # Frontend
   cd frontend && npm install

   # Backend
   cd ../backend && pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   # Frontend
   cp frontend/.env.example frontend/.env.local

   # Backend
   cp backend/.env.example backend/.env

   # AI Engine (optional)
   cp ai-engine/.env.example ai-engine/.env
   ```

4. **Start development servers**

   ```bash
   # Terminal 1: Backend
   cd backend && python -m app.main

   # Terminal 2: Frontend
   cd frontend && npm run dev

   # Terminal 3: AI Engine (optional)
   cd ai-engine && python main.py
   ```

5. **VSCode Extension (optional)**

   ```bash
   # Install extension in development mode
   cd extension
   npm install
   npm run compile
   # Then press F5 in VSCode to run extension
   ```

6. **Open your browser**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000/docs`

---

## 🎮 **Demo & Features**

### **Smart Focus Timer**

- **Pomodoro Technique**: 25-minute focus sessions with 5-minute breaks
- **Activity Tracking**: Real-time monitoring of keyboard and mouse activity
- **Idle Detection**: Automatic detection of inactivity with visual indicators
- **Progress Visualization**: Circular progress bar with session statistics

### **Mood & Productivity Analytics**

- **Post-Session Tracking**: Modal after each focus session
- **Multi-Dimensional Metrics**: Mood (1-5), Energy (1-5), Stress (1-5)
- **Correlation Analysis**: Understand relationships between mood and productivity
- **Historical Trends**: Track patterns over time with beautiful charts

### **VSCode Extension Integration**

- **Real-time Activity Tracking**: Monitors file changes and coding sessions
- **Productivity Sidebar**: Live metrics panel with daily statistics
- **Git Integration**: Automatic repository and branch context detection
- **Session Management**: Smart idle detection and session boundaries
- **Offline Support**: Works without internet, syncs when available

### **GitHub App Integration**

- **Automatic Webhook Processing**: Handles push, PR, and review events
- **AI-Powered Commit Analysis**: GPT-based analysis of commit quality and patterns
- **Security**: GitHub signature verification and secure webhook handling
- **Activity Correlation**: Links GitHub activity with productivity sessions

### **Offline-First Architecture**

- **Complete Offline Support**: Works without internet connection
- **Automatic Sync**: Data synchronizes when connection is restored
- **Network Status Indicators**: Visual feedback for online/offline state
- **Data Persistence**: localStorage with intelligent sync mechanisms

---

## 🛠️ **Development Roadmap**

### **✅ Completed Stages**

- **Stage 1**: Project setup and architecture design
- **Stage 2**: Backend API with authentication and database
- **Stage 3**: Smart Focus Timer with mood tracking
- **Stage 4**: AI-powered activity analysis and commit insights
- **Stage 5**: GitHub App integration and VSCode extension

### **🚧 Current Development**

- **Stage 6**: Desktop application enhancement with Tauri

### **📋 Planned Features**

- **Enhanced Team Analytics**: Collaborative productivity insights
- **Calendar Integration**: Meeting and schedule awareness
- **Custom Workflows**: Personalized productivity patterns
- **Export & Reporting**: Comprehensive productivity reports
- **Mobile App**: React Native productivity companion

---

## 🚀 **Deployment**

### **Production Ready**

- **Frontend**: Vercel deployment configured
- **Backend**: Railway deployment with PostgreSQL
- **Database**: Production-ready with migrations
- **Authentication**: Supabase integration complete
- **Monitoring**: Health checks and logging implemented

### **Environment Support**

- **Development**: Local development with hot reload
- **Staging**: Testing environment with real data
- **Production**: Scalable cloud deployment

---

## 🤝 **Contributing**

This project is currently in **active development**. Contributions, suggestions, and feedback are welcome!

### **Development Guidelines**

- **Code Quality**: TypeScript throughout, ESLint configured
- **Testing**: Jest and Playwright test suites
- **Documentation**: Comprehensive API documentation
- **Git Workflow**: Feature branches with pull requests

---

## 👨‍💻 **For Recruiters & Collaborators**

### **Technical Highlights**

- **Full-Stack Expertise**: Modern web technologies with production deployment
- **System Architecture**: Scalable monorepo with microservices approach
- **Database Design**: Normalized PostgreSQL with proper relationships
- **API Development**: RESTful APIs with authentication and security
- **Frontend Excellence**: React 19 with TypeScript and modern UI patterns
- **Desktop Development**: Cross-platform with Rust and Tauri
- **DevOps**: Docker, Railway, Vercel deployment pipelines

### **Project Scale**

- **25+ API endpoints** with full CRUD operations
- **30+ React components** with TypeScript
- **8+ database models** with relationships
- **Complete VSCode extension** with 600+ lines of TypeScript
- **AI-powered analysis engine** with GPT integration
- **GitHub App integration** with webhook processing
- **Offline-first architecture** with sync mechanisms
- **Production deployment** configuration
- **Comprehensive testing** strategy

### **Skills Demonstrated**

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, JWT Authentication
- **Frontend**: React, Next.js, TypeScript, Tailwind CSS, Chart.js
- **Desktop**: Rust, Tauri, Cross-platform development
- **VSCode Extension**: TypeScript, VSCode API, Real-time tracking
- **AI/ML**: OpenAI GPT integration, Natural language processing
- **GitHub Integration**: Webhooks, App development, API integration
- **DevOps**: Docker, Railway, Vercel, Environment management
- **Database**: PostgreSQL, SQLAlchemy ORM, Database design
- **API**: RESTful design, OpenAPI documentation, Rate limiting
- **Security**: JWT tokens, CORS, Input validation, Webhook signatures

---

## 📊 **Project Status**

| Component              | Status        | Progress | Description                      |
| ---------------------- | ------------- | -------- | -------------------------------- |
| **Backend API**        | ✅ Complete   | 100%     | FastAPI with full authentication |
| **Frontend App**       | ✅ Complete   | 100%     | Next.js with focus timer         |
| **Database**           | ✅ Complete   | 100%     | PostgreSQL with models           |
| **Authentication**     | ✅ Complete   | 100%     | Supabase integration             |
| **AI Engine**          | ✅ Complete   | 100%     | GPT-powered commit analysis      |
| **GitHub Integration** | ✅ Complete   | 100%     | Webhook processing & analysis    |
| **VS Code Extension**  | ✅ Complete   | 100%     | Full productivity tracking       |
| **Desktop App**        | � In Progress | 30%      | Tauri foundation                 |

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 **Contact**

**Project Status**: Active Development  
**Stage**: 5 Complete (GitHub & VSCode Integration)  
**Next Milestone**: Enhanced Desktop Application

For questions, collaboration, or recruitment inquiries, please reach out through GitHub Issues or direct contact.

---

_Last Updated: June 15, 2025_
