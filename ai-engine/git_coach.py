#!/usr/bin/env python3
"""
AI Code Coach - Daily Git Analysis Script
Analyzes last 24 hours of git activity and generates AI-powered insights.
Supports both OpenAI and Groq APIs for flexibility and speed.
"""

import os
import subprocess
import json
import openai
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from db_client import DatabaseClient

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq library not installed. Install with: pip install groq")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitCoach:
    def __init__(self, repo_path: str = ".", openai_api_key: Optional[str] = None, groq_api_key: Optional[str] = None, prefer_groq: bool = True):
        self.repo_path = repo_path
        self.db = DatabaseClient()
        self.prefer_groq = prefer_groq
        self.groq_client = None
        self.openai_available = False
        self.groq_available = False

        # Initialize Groq
        if GROQ_AVAILABLE:
            if groq_api_key:
                self.groq_api_key = groq_api_key
            else:
                self.groq_api_key = os.getenv("GROQ_API_KEY")
            
            if self.groq_api_key:
                try:
                    self.groq_client = Groq(api_key=self.groq_api_key)
                    self.groq_available = True
                    logger.info("Groq API initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize Groq client: {e}")

        # Initialize OpenAI
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
        if openai.api_key:
            self.openai_available = True
            logger.info("OpenAI API initialized successfully")

        # Check if at least one API is available
        if not self.groq_available and not self.openai_available:
            raise ValueError(
                "No AI API available. Set either GROQ_API_KEY or OPENAI_API_KEY environment variable."
            )
        
        # Log which APIs will be used
        if self.groq_available and self.openai_available:
            primary = "Groq" if self.prefer_groq else "OpenAI"
            fallback = "OpenAI" if self.prefer_groq else "Groq"
            logger.info(f"Both APIs available. Primary: {primary}, Fallback: {fallback}")
        elif self.groq_available:
            logger.info("Using Groq API only")
        else:
            logger.info("Using OpenAI API only")

    def get_git_activity(self, hours: int = 24) -> Dict:
        """Get git commits and changes from the last N hours."""
        try:
            # Calculate time threshold
            since_time = datetime.now() - timedelta(hours=hours)
            since_str = since_time.strftime("%Y-%m-%d %H:%M:%S")

            # Get commit log
            cmd_log = [
                "git",
                "log",
                f'--since="{since_str}"',
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso",
            ]

            result_log = subprocess.run(
                cmd_log, cwd=self.repo_path, capture_output=True, text=True
            )

            if result_log.returncode != 0:
                logger.error(f"Git log failed: {result_log.stderr}")
                return {"commits": [], "stats": {}}

            # Parse commits
            commits = []
            if result_log.stdout.strip():
                for line in result_log.stdout.strip().split("\n"):
                    parts = line.split("|", 4)
                    if len(parts) == 5:
                        commits.append(
                            {
                                "hash": parts[0],
                                "author": parts[1],
                                "email": parts[2],
                                "date": parts[3],
                                "message": parts[4],
                            }
                        )

            # Get diff stats
            if commits:
                cmd_stats = [
                    "git",
                    "diff",
                    "--stat",
                    f'{commits[-1]["hash"]}~1..{commits[0]["hash"]}',
                ]

                result_stats = subprocess.run(
                    cmd_stats, cwd=self.repo_path, capture_output=True, text=True
                )

                stats = {
                    "files_changed": 0,
                    "insertions": 0,
                    "deletions": 0,
                    "diff_output": (
                        result_stats.stdout if result_stats.returncode == 0 else ""
                    ),
                }

                # Parse basic stats from diff output
                if result_stats.stdout:
                    lines = result_stats.stdout.strip().split("\n")
                    for line in lines:
                        if "files changed" in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "files" and i > 0:
                                    stats["files_changed"] = int(parts[i - 1])
                                elif part == "insertions(+)" and i > 0:
                                    stats["insertions"] = int(parts[i - 1])
                                elif part == "deletions(-)" and i > 0:
                                    stats["deletions"] = int(parts[i - 1])
            else:
                stats = {
                    "files_changed": 0,
                    "insertions": 0,
                    "deletions": 0,
                    "diff_output": "",
                }

            return {
                "commits": commits,
                "stats": stats,
                "analysis_time": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting git activity: {e}")
            return {"commits": [], "stats": {}}

    def analyze_with_ai(self, git_data: Dict) -> Dict:
        """Use OpenAI or Groq to analyze git activity and provide insights."""
        try:
            if not git_data["commits"]:
                return {
                    "summary": "No git activity found in the last 24 hours.",
                    "suggestions": [
                        "Consider making regular commits to track your progress."
                    ],
                    "tags": ["#no-activity"],
                    "productivity_score": 0,
                }

            # Prepare context for AI
            commit_messages = [commit["message"] for commit in git_data["commits"]]
            stats = git_data["stats"]

            prompt = f"""
            Analyze the following git activity from the last 24 hours and provide insights:
            
            Commits ({len(commit_messages)} total):
            {chr(10).join(f"- {msg}" for msg in commit_messages[:10])}
            
            Statistics:
            - Files changed: {stats.get('files_changed', 0)}
            - Lines added: {stats.get('insertions', 0)}
            - Lines deleted: {stats.get('deletions', 0)}
            
            Please provide a JSON response with:
            1. "summary": A natural language summary of the work done
            2. "suggestions": Array of 2-3 specific improvement suggestions
            3. "tags": Array of relevant tags like #feature, #bugfix, #refactor, #documentation
            4. "productivity_score": A score from 1-10 based on activity level
            
            Focus on being constructive and specific. Look for patterns in commit messages.
            """

            # Try Groq first if preferred
            if self.groq_available and self.prefer_groq:
                response = self._call_groq_api(prompt, "You are an AI code coach helping developers improve their productivity and code quality. Respond only with valid JSON.")
            # Fallback to OpenAI
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI code coach helping developers improve their productivity and code quality. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )

            # Parse AI response
            ai_response = response.choices[0].message.content.strip()

            # Try to parse as JSON
            analysis = self._parse_ai_response(ai_response, git_data)

            return analysis

        except Exception as e:
            logger.error(f"Error with AI analysis: {e}")
            return self._get_fallback_analysis(git_data)

    def _call_groq_api(self, prompt: str, system_message: str) -> Optional[str]:
        """Call Groq API for analysis."""
        if not self.groq_client:
            return None
            
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Fast and capable model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return None

    def _parse_ai_response(self, ai_response: str, git_data: Dict) -> Dict:
        """Parse AI response and validate required fields."""
        try:
            analysis = json.loads(ai_response)

            # Validate required fields
            required_fields = [
                "summary",
                "suggestions",
                "tags",
                "productivity_score",
            ]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = self._get_default_value(field)

            # Ensure suggestions and tags are arrays
            if not isinstance(analysis["suggestions"], list):
                analysis["suggestions"] = [str(analysis["suggestions"])]
            if not isinstance(analysis["tags"], list):
                analysis["tags"] = [str(analysis["tags"])]

            return analysis

        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {ai_response}")
            return self._get_fallback_analysis(git_data)

    def _get_default_value(self, field: str):
        """Get default values for missing fields."""
        defaults = {
            "summary": "Development activity detected.",
            "suggestions": ["Keep up the good work!"],
            "tags": ["#development"],
            "productivity_score": 5,
        }
        return defaults.get(field, "")

    def _get_fallback_analysis(self, git_data: Dict) -> Dict:
        """Provide fallback analysis when AI fails."""
        commit_count = len(git_data["commits"])
        files_changed = git_data["stats"].get("files_changed", 0)

        return {
            "summary": f"You made {commit_count} commits affecting {files_changed} files today.",
            "suggestions": [
                "Consider adding more descriptive commit messages.",
                "Regular commits help track progress better.",
            ],
            "tags": ["#development", "#commits"],
            "productivity_score": min(commit_count * 2, 10),
        }

    def save_review(self, user_id: str, analysis: Dict) -> bool:
        """Save AI review to database."""
        try:
            query = """
            INSERT INTO ai_reviews (user_id, summary, suggestions, tags, productivity_score, reviewed_at)
            VALUES (%(user_id)s, %(summary)s, %(suggestions)s, %(tags)s, %(productivity_score)s, NOW())
            """

            params = {
                "user_id": user_id,
                "summary": analysis["summary"],
                "suggestions": analysis["suggestions"],
                "tags": analysis["tags"],
                "productivity_score": analysis.get("productivity_score", 5),
            }

            success = self.db.execute_query(query, params)
            if success:
                logger.info(f"Saved AI review for user {user_id}")
            return success

        except Exception as e:
            logger.error(f"Error saving review: {e}")
            return False

    def run_daily_analysis(self, user_id: str) -> Dict:
        """Run complete daily analysis pipeline."""
        logger.info(f"Starting daily analysis for user {user_id}")

        # Get git activity
        git_data = self.get_git_activity()

        # Analyze with AI
        analysis = self.analyze_with_ai(git_data)

        # Save to database
        saved = self.save_review(user_id, analysis)

        result = {
            "success": saved,
            "analysis": analysis,
            "git_data": git_data,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Daily analysis completed. Success: {saved}")
        return result


def main():
    """CLI entry point for daily analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Code Coach - Daily Git Analysis")
    parser.add_argument("--user-id", required=True, help="User ID for database storage")
    parser.add_argument("--repo-path", default=".", help="Path to git repository")
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours of history to analyze"
    )
    parser.add_argument(
        "--prefer-openai", action="store_true", 
        help="Prefer OpenAI over Groq when both APIs are available"
    )

    args = parser.parse_args()

    try:
        coach = GitCoach(
            repo_path=args.repo_path,
            prefer_groq=not args.prefer_openai
        )
        result = coach.run_daily_analysis(args.user_id)

        print(json.dumps(result, indent=2))

        if result["success"]:
            exit(0)
        else:
            exit(1)

    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
