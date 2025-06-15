#!/usr/bin/env python3
"""
DevScope AI Activity Analyzer - Enhanced CLI Tool

This script orchestrates the complete AI analysis pipeline:
1. Parse recent Git commits and diffs
2. Analyze commits using OpenAI GPT
3. Store results in the backend database
4. Handle offline caching and rate limiting

Usage:
    python cli_analyzer.py [--hours=24] [--dry-run] [--verbose]
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
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
        
        # Check if we should use mock analysis
        openai_api_key = os.getenv('OPENAI_API_KEY')
        use_mock = not openai_api_key or openai_api_key == 'test-key-for-development'
        if use_mock:
            print("⚠️  Using mock analysis (OpenAI API key not configured)")
        
        # Mock analysis function
        def mock_analysis(commit):
            """Generate mock analysis for testing."""
            message = commit['message'].lower()
            
            if 'fix' in message or 'bug' in message:
                return {"label": "Bug Fixing", "confidence": 0.85, "reasoning": "Commit message indicates bug fixing"}
            elif 'refactor' in message or 'clean' in message:
                return {"label": "Refactoring", "confidence": 0.82, "reasoning": "Code improvement and refactoring"}
            elif 'feat' in message or 'add' in message:
                return {"label": "High Focus", "confidence": 0.88, "reasoning": "New feature development"}
            elif 'test' in message:
                return {"label": "Testing", "confidence": 0.80, "reasoning": "Test implementation"}
            elif 'doc' in message or 'readme' in message:
                return {"label": "Documentation", "confidence": 0.83, "reasoning": "Documentation updates"}
            else:
                return {"label": "General Development", "confidence": 0.75, "reasoning": "General development work"}
        
        # Step 2: Analyze commits with AI or mock
        print(f"\n🧠 Step 2: {'Mock analyzing' if use_mock else 'Analyzing'} commits with {'test classifier' if use_mock else 'AI'}...")
        
        analyzed_commits = []
        for i, commit in enumerate(commits, 1):
            print(f"Analyzing commit {i}/{len(commits)}: {commit['short_id']}")
            
            try:
                if use_mock:
                    # Use mock analysis
                    analysis_result = mock_analysis(commit)
                    print(f"  ✅ Mock classified as: {analysis_result['label']} (confidence: {analysis_result['confidence']:.2f})")
                else:
                    # Use real OpenAI analysis
                    analysis_result = await analyzer.analyze_commit(commit)
                    if analysis_result:
                        print(f"  ✅ AI classified as: {analysis_result['label']} (confidence: {analysis_result['confidence']:.2f})")
                    else:
                        print(f"  ⚠️ Failed to analyze commit")
                        continue
                
                # Store successful analysis
                analyzed_commits.append({
                    'commit_sha': commit['id'],
                    'commit_message': commit['message'],
                    'commit_author': commit['author'],
                    'commit_date': commit['timestamp'],
                    'analysis': analysis_result,
                    'analyzed_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"  ❌ Error analyzing commit: {e}")
                continue
                
            except Exception as e:
                print(f"  ❌ Error analyzing commit: {str(e)}")
        
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
