# 🧠 DevScope AI Activity Analyzer

## 🎯 Overview

The AI Activity Analyzer is an intelligent system that automatically analyzes Git commits using OpenAI's GPT models to classify developer productivity patterns and contexts. It's part of Stage 4 of the DevScope platform.

## ✨ Features

- **🔍 Git Analysis**: Parses commit messages, diffs, and metadata
- **🧠 AI Classification**: Uses OpenAI GPT to classify productivity contexts
- **📊 Smart Categorization**: 10+ productivity categories including High Focus, Bug Fixing, Refactoring, Research Spike, Documentation, Testing, and more
- **💾 Offline Support**: Caches results when backend unavailable
- **⚡ Rate Limiting**: Respects OpenAI API limits (3 req/min, $5/month)
- **🔄 Automated Scheduling**: Cron job integration for continuous analysis
- **🎭 Mock Mode**: Test mode when OpenAI API key not available

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd ai-engine/
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Analysis

```bash
# Test with mock analysis
python cli_analyzer.py

# Real analysis (requires OpenAI API key)
python cli_analyzer.py --hours=24
```

### 4. Setup Automated Analysis

```bash
# Install cron job (runs every 30 min, 9 AM - 6 PM, weekdays)
./setup_cron.sh

# Manual execution
./run_analyzer.sh
```

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
