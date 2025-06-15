#!/bin/bash
# DevScope AI Analyzer - Cron Job Setup Script
#
# This script sets up automated analysis of Git commits using cron jobs.
# It can be run every 30 minutes to analyze recent commits automatically.

# Set up the environment
export REPO_PATH="/workspaces/DevScope"
export AI_ENGINE_PATH="/workspaces/DevScope/ai-engine"

# Change to AI engine directory
cd "$AI_ENGINE_PATH"

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the analyzer
echo "🚀 Starting automated Git analysis at $(date)"
python3 cli_analyzer.py --hours=1

# Log completion
echo "✅ Analysis completed at $(date)"
echo "---"
