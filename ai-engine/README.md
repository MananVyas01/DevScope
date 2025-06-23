# 🧠 DevScope AI Activity Analyzer

## 🎯 Overview

The AI Activity Analyzer is an intelligent system that automatically analyzes Git commits using OpenAI's GPT models to classify developer productivity patterns and contexts. It's part of Stage 4 of the DevScope platform.

## ✨ Features

- **🔍 Git Analysis**: Parses commit messages, diffs, and metadata
- **🧠 AI Classification**: Uses OpenAI GPT or Groq Llama models to classify productivity contexts
- **⚡ Groq Support**: Ultra-fast inference with Groq's optimized hardware (default)
- **� API Fallback**: Automatic fallback between Groq and OpenAI APIs
- **�📊 Smart Categorization**: 10+ productivity categories including High Focus, Bug Fixing, Refactoring, Research Spike, Documentation, Testing, and more
- **💾 Offline Support**: Caches results when backend unavailable
- **⚡ Rate Limiting**: Respects API limits
- **🔄 Automated Scheduling**: Cron job integration for continuous analysis
- **🎭 Mock Mode**: Test mode when no API key is available

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd ai-engine/
cp .env.example .env
# Edit .env with your API keys:
# GROQ_API_KEY=your_groq_key_here (recommended - faster & cheaper)
# OPENAI_API_KEY=your_openai_key_here (fallback)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Analysis

```bash
# Test with mock analysis
python cli_analyzer.py

# Real analysis with Groq (default, faster)
python git_coach.py --user-id=test-user --hours=24

# Force OpenAI usage
python git_coach.py --user-id=test-user --hours=24 --prefer-openai
```

### 4. Setup Automated Analysis

```bash
# Install cron job (runs every 30 min, 9 AM - 6 PM, weekdays)
./setup_cron.sh

# Manual execution
./run_analyzer.sh
```

## 🚀 Why Groq?

Groq offers several advantages as the default AI provider:

- **⚡ Speed**: 5-10x faster inference than OpenAI (typically <1 second)
- **💰 Cost**: Significantly cheaper per token
- **🎯 Quality**: Llama 3.1 70B provides excellent code analysis
- **🔄 Reliability**: High uptime and rate limits
- **🛡️ Fallback**: Automatic OpenAI fallback ensures reliability

Set your `GROQ_API_KEY` environment variable to get started!

## 📊 Sample Output

```
🧠 Step 2: Mock analyzing commits with test classifier...
Analyzing commit 1/5: b939b15c
  ✅ Mock classified as: High Focus (confidence: 0.88)
Analyzing commit 2/5: f04387de
  ✅ Mock classified as: Bug Fixing (confidence: 0.85)

📊 Analysis Summary:
  • Commits processed: 5
  • Successfully analyzed: 5
  • Stored in database: 5
  • OpenAI requests made: 5
  • Estimated cost: $0.0150
```

## 🎯 Classification Categories

| Category           | Description               | Example Commits                          |
| ------------------ | ------------------------- | ---------------------------------------- |
| **High Focus**     | New feature development   | "feat: implement user dashboard"         |
| **Bug Fixing**     | Fixing issues and bugs    | "fix: resolve login validation error"    |
| **Refactoring**    | Code improvement          | "refactor: optimize database queries"    |
| **Research Spike** | Exploration and learning  | "spike: investigate GraphQL integration" |
| **Documentation**  | Writing docs and comments | "docs: update API documentation"         |
| **Testing**        | Adding or fixing tests    | "test: add unit tests for auth module"   |

---

**Stage 4 Complete** ✅ - The AI Activity Analyzer is ready for production use!
