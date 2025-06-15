#!/usr/bin/env python3
"""
DevScope AI Activity Analyzer - CLI Tool

This script analyzes Git commit logs and diffs using OpenAI GPT to classify
developer productivity patterns and contexts.

Stage 4: AI Activity Analyzer
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import CommitAnalyzer
from git_parser import GitLogParser
from db_client import BackendAPIClient


async def main():
    """Main analysis pipeline."""
    print("🚀 DevScope AI Activity Analyzer - Stage 4")
    print("=" * 50)
    
    # Initialize components
    git_parser = GitLogParser(
        repo_path=os.getenv('REPO_PATH', '../'),
        hours_back=int(os.getenv('ANALYSIS_HOURS_BACK', 24))
    )
    
    analyzer = CommitAnalyzer(
        api_key=os.getenv('OPENAI_API_KEY'),
        max_requests_per_minute=int(os.getenv('MAX_REQUESTS_PER_MINUTE', 3)),
        monthly_budget=float(os.getenv('MAX_MONTHLY_BUDGET', 5.0))
    )
    
    db_client = BackendAPIClient(
        base_url=os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1'),
        api_key=os.getenv('BACKEND_API_KEY')
    )
    
    try:
        # Step 1: Parse recent commits
        print("\n📋 Step 1: Parsing Git commits...")
        commits = git_parser.get_recent_commits()
        print(f"Found {len(commits)} commits to analyze")
        
        if not commits:
            print("✅ No new commits to analyze")
            return
        
        # Step 2: Analyze commits with AI
        print("\n🧠 Step 2: Analyzing commits with AI...")
        analyzed_commits = []
        
        for i, commit in enumerate(commits):
            print(f"Analyzing commit {i+1}/{len(commits)}: {commit['id'][:8]}")
            
            analysis = await analyzer.analyze_commit(commit)
            if analysis:
                analyzed_commits.append({
                    **commit,
                    'analysis': analysis
                })
                print(f"  ✅ Classified as: {analysis['label']} (confidence: {analysis['confidence']:.2f})")
            else:
                print(f"  ⚠️ Failed to analyze commit")
        
        # Step 3: Store results in database
        print(f"\n💾 Step 3: Storing {len(analyzed_commits)} analysis results...")
        
        success_count = 0
        for commit_data in analyzed_commits:
            if await db_client.store_analysis(commit_data):
                success_count += 1
        
        print(f"✅ Successfully stored {success_count}/{len(analyzed_commits)} analyses")
        
        # Step 4: Cleanup and summary
        print("\n📊 Analysis Summary:")
        print(f"  • Commits processed: {len(commits)}")
        print(f"  • Successfully analyzed: {len(analyzed_commits)}")
        print(f"  • Stored in database: {success_count}")
        print(f"  • OpenAI requests made: {analyzer.get_request_count()}")
        print(f"  • Estimated cost: ${analyzer.get_estimated_cost():.4f}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        raise
    finally:
        # Cleanup
        await analyzer.cleanup()
        await db_client.cleanup()


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please copy .env.example to .env and configure the required values")
        sys.exit(1)
    
    # Run the analysis
    asyncio.run(main())
