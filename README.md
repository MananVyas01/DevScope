# 🎯 DevScope - Developer Productivity, Reimagined

[![Development Stage](https://img.shields.io/badge/Status-Stage%203%20Complete-success?style=for-the-badge)](#-current-development-stage)
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

### **VS Code Extension** (Planned 📋)

- **Language**: TypeScript
- **Integration**: VS Code API
- **Features**: Workflow tracking, time analytics

### **AI Engine** (Planned 🤖)

- **Language**: Python
- **ML Libraries**: TensorFlow/PyTorch
- **Features**: Productivity insights, pattern recognition

---

## 🎯 **Current Development Stage**

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
├── 🔌 extension/         # VS Code extension (📋 Planned)
│   └── src/              # TypeScript extension
│
└── 🤖 ai-engine/         # ML analytics (📋 Planned)
    └── src/              # Python ML pipeline
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
   ```

4. **Start development servers**

   ```bash
   # Terminal 1: Backend
   cd backend && python -m app.main

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

5. **Open your browser**
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

### **🚧 Current Development**

- **Stage 4**: Desktop application with Tauri
- **Stage 5**: VS Code extension integration
- **Stage 6**: AI-powered productivity insights

### **📋 Planned Features**

- **GitHub Integration**: Automatic commit and PR activity tracking
- **Team Analytics**: Collaborative productivity insights
- **Calendar Integration**: Meeting and schedule awareness
- **Custom Workflows**: Personalized productivity patterns
- **Export & Reporting**: Comprehensive productivity reports

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

- **10+ API endpoints** with full CRUD operations
- **20+ React components** with TypeScript
- **5+ database models** with relationships
- **Offline-first architecture** with sync mechanisms
- **Production deployment** configuration
- **Comprehensive testing** strategy

### **Skills Demonstrated**

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, JWT Authentication
- **Frontend**: React, Next.js, TypeScript, Tailwind CSS, Chart.js
- **Desktop**: Rust, Tauri, Cross-platform development
- **DevOps**: Docker, Railway, Vercel, Environment management
- **Database**: PostgreSQL, SQLAlchemy ORM, Database design
- **API**: RESTful design, OpenAPI documentation, Rate limiting
- **Security**: JWT tokens, CORS, Input validation, Rate limiting

---

## 📊 **Project Status**

| Component             | Status         | Progress | Description                      |
| --------------------- | -------------- | -------- | -------------------------------- |
| **Backend API**       | ✅ Complete    | 100%     | FastAPI with full authentication |
| **Frontend App**      | ✅ Complete    | 100%     | Next.js with focus timer         |
| **Database**          | ✅ Complete    | 100%     | PostgreSQL with models           |
| **Authentication**    | ✅ Complete    | 100%     | Supabase integration             |
| **Desktop App**       | 🚧 In Progress | 30%      | Tauri foundation                 |
| **VS Code Extension** | 📋 Planned     | 10%      | Basic structure                  |
| **AI Engine**         | 📋 Planned     | 5%       | Requirements defined             |

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 **Contact**

**Project Status**: Active Development  
**Stage**: 3 Complete (Production Ready Focus Timer)  
**Next Milestone**: Desktop Application Development

For questions, collaboration, or recruitment inquiries, please reach out through GitHub Issues or direct contact.

---

_Last Updated: June 15, 2025_
