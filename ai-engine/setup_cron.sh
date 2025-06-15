#!/bin/bash
# DevScope AI Analyzer - Cron Job Installer
#
# This script installs a cron job to automatically analyze Git commits
# every 30 minutes during development hours (9 AM - 6 PM).

echo "🔧 Setting up DevScope AI Analyzer cron job..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ANALYZER_SCRIPT="$SCRIPT_DIR/run_analyzer.sh"

# Create cron job entry
CRON_JOB="*/30 9-18 * * 1-5 $ANALYZER_SCRIPT >> $SCRIPT_DIR/analyzer.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_analyzer.sh"; then
    echo "⚠️  Cron job already exists. Remove it first if you want to reinstall."
    echo "   Use: crontab -e"
    exit 1
fi

# Add cron job
echo "📋 Adding cron job: $CRON_JOB"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed successfully!"
echo "   Schedule: Every 30 minutes, Monday-Friday, 9 AM - 6 PM"
echo "   Log file: $SCRIPT_DIR/analyzer.log"
echo ""
echo "🔍 To check status:"
echo "   crontab -l"
echo ""
echo "🗑️  To remove:"
echo "   crontab -e"
echo ""
echo "📊 To test manually:"
echo "   $ANALYZER_SCRIPT"
