"""
Commit Analyzer using OpenAI GPT for DevScope AI Activity Analyzer

This module handles the AI analysis of Git commits using OpenAI's GPT models
to classify developer productivity patterns and contexts.
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import openai
from openai import AsyncOpenAI
import os


class CommitAnalyzer:
    """Analyzes Git commits using OpenAI GPT to classify productivity patterns."""

    # Productivity classification labels
    PRODUCTIVITY_LABELS = [
        "High Focus",
        "Distracted",
        "Refactoring",
        "Bug Fixing",
        "Research Spike",
        "Feature Development",
        "Testing",
        "Documentation",
        "Code Review",
        "Setup/Configuration",
    ]

    def __init__(
        self,
        api_key: str,
        max_requests_per_minute: int = 3,
        monthly_budget: float = 5.0,
    ):
        """
        Initialize the commit analyzer.

        Args:
            api_key: OpenAI API key
            max_requests_per_minute: Rate limit for API calls
            monthly_budget: Maximum monthly spending limit in USD
        """
        self.api_key = api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.monthly_budget = monthly_budget

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)

        # Rate limiting
        self.request_times = []
        self.request_count = 0
        self.estimated_cost = 0.0

        # Load cache
        self.cache_file = os.getenv(
            "OFFLINE_CACHE_FILE", "./cache/offline_analysis.json"
        )
        self.cache = self._load_cache()

        print(
            f"🧠 CommitAnalyzer initialized with {max_requests_per_minute} req/min limit"
        )

    async def analyze_commit(self, commit_data: Dict) -> Optional[Dict]:
        """
        Analyze a single commit using OpenAI GPT.

        Args:
            commit_data: Dictionary containing commit information

        Returns:
            Analysis result with label and confidence, or None if failed
        """
        commit_id = commit_data.get("id", "unknown")

        # Check cache first
        if commit_id in self.cache:
            print(f"  📄 Using cached analysis for {commit_id[:8]}")
            return self.cache[commit_id]

        # Check rate limits
        if not await self._check_rate_limits():
            print(f"  ⚠️ Rate limit exceeded, skipping {commit_id[:8]}")
            return None

        # Check budget
        if not self._check_budget():
            print(f"  💰 Monthly budget exceeded, skipping {commit_id[:8]}")
            return None

        try:
            # Build the prompt
            prompt = self._build_analysis_prompt(commit_data)

            # Make the API call
            response = await self._call_openai_api(prompt)

            if response:
                # Cache the result
                self.cache[commit_id] = response
                self._save_cache()

                # Update cost tracking
                self._update_cost_tracking()

                return response

        except Exception as e:
            print(f"  ❌ Error analyzing commit {commit_id[:8]}: {e}")

        return None

    def _build_analysis_prompt(self, commit_data: Dict) -> str:
        """
        Build a comprehensive prompt for OpenAI analysis.

        Args:
            commit_data: Commit information dictionary

        Returns:
            Formatted prompt string
        """
        commit_message = commit_data.get("message", "")
        diff_content = commit_data.get("diff", "")
        files_changed = commit_data.get("files_changed", [])
        stats = commit_data.get("stats", {})
        commit_type = commit_data.get("commit_type", "other")

        # Truncate diff if too long (to stay within token limits)
        if len(diff_content) > 3000:
            diff_content = diff_content[:3000] + "\n... (truncated for analysis)"

        # Build file list
        file_list = ", ".join(
            [f["path"] for f in files_changed[:10]]
        )  # Limit to 10 files
        if len(files_changed) > 10:
            file_list += f" ... and {len(files_changed) - 10} more files"

        prompt = f"""Analyze this Git commit and classify the developer's productivity context.

COMMIT INFORMATION:
- Message: "{commit_message}"
- Files changed: {file_list}
- Statistics: +{stats.get('additions', 0)} additions, -{stats.get('deletions', 0)} deletions, {stats.get('files_changed', 0)} files
- Detected type: {commit_type}

CODE DIFF:
{diff_content}

TASK:
Based on the commit message, code changes, and diff patterns, classify this commit into ONE of these productivity contexts:

{chr(10).join(f"- {label}" for label in self.PRODUCTIVITY_LABELS)}

Consider these factors:
1. Commit message intent and clarity
2. Code change patterns (additions vs deletions vs modifications)
3. File types and locations modified
4. Size and scope of changes
5. Whether changes suggest focused work vs exploratory work

RESPONSE FORMAT:
Respond with a JSON object containing:
{{
  "label": "one of the productivity labels above",
  "confidence": confidence_score_between_0_and_1,
  "reasoning": "brief explanation of why this classification was chosen",
  "indicators": ["key", "factors", "that", "influenced", "decision"]
}}

Example:
{{
  "label": "Bug Fixing",
  "confidence": 0.85,
  "reasoning": "Commit message indicates fixing an issue, small targeted changes in error handling code",
  "indicators": ["fix keyword in message", "small targeted changes", "error handling modifications"]
}}"""

        return prompt

    async def _call_openai_api(self, prompt: str) -> Optional[Dict]:
        """
        Make the actual OpenAI API call.

        Args:
            prompt: The analysis prompt

        Returns:
            Parsed analysis result or None if failed
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using cheaper model for budget
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software development productivity analyst. Analyze Git commits to understand developer productivity patterns and work contexts. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=300,  # Limit response size
                timeout=30.0,  # 30 second timeout
            )

            # Parse the response
            content = response.choices[0].message.content.strip()

            # Try to parse JSON response
            try:
                analysis = json.loads(content)

                # Validate the response structure
                if self._validate_analysis_response(analysis):
                    self.request_count += 1
                    return analysis
                else:
                    print(f"  ⚠️ Invalid response structure: {content[:100]}...")
                    return None

            except json.JSONDecodeError:
                print(f"  ⚠️ Failed to parse JSON response: {content[:100]}...")
                return None

        except Exception as e:
            print(f"  ❌ OpenAI API error: {e}")
            return None

    def _validate_analysis_response(self, analysis: Dict) -> bool:
        """Validate that the analysis response has the required structure."""
        required_fields = ["label", "confidence", "reasoning"]

        if not all(field in analysis for field in required_fields):
            return False

        if analysis["label"] not in self.PRODUCTIVITY_LABELS:
            return False

        if not isinstance(analysis["confidence"], (int, float)) or not (
            0 <= analysis["confidence"] <= 1
        ):
            return False

        return True

    async def _check_rate_limits(self) -> bool:
        """Check if we can make another API request without exceeding rate limits."""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Check if we're under the rate limit
        if len(self.request_times) >= self.max_requests_per_minute:
            # Calculate how long to wait
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                print(f"  ⏳ Rate limit reached, waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                return await self._check_rate_limits()  # Recursive check after waiting

        # Record this request time
        self.request_times.append(now)
        return True

    def _check_budget(self) -> bool:
        """Check if we're still within the monthly budget."""
        # Rough estimate: GPT-3.5-turbo costs ~$0.002 per 1K tokens
        # Our prompts are roughly 1-2K tokens, responses ~300 tokens
        # Estimate ~$0.005 per request
        estimated_request_cost = 0.005

        if self.estimated_cost + estimated_request_cost > self.monthly_budget:
            return False

        return True

    def _update_cost_tracking(self):
        """Update the estimated cost after a successful API call."""
        self.estimated_cost += 0.005  # Rough estimate per request

    def _load_cache(self) -> Dict:
        """Load cached analysis results."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")

        return {}

    def _save_cache(self):
        """Save analysis results to cache."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving cache: {e}")

    def get_request_count(self) -> int:
        """Get the number of API requests made."""
        return self.request_count

    def get_estimated_cost(self) -> float:
        """Get the estimated cost of API requests."""
        return self.estimated_cost

    async def cleanup(self):
        """Cleanup resources."""
        # Save final cache state
        self._save_cache()

        # Close OpenAI client if needed
        if hasattr(self.client, "close"):
            await self.client.close()


# Test function for development
if __name__ == "__main__":

    async def test_analyzer():
        print("🧠 Testing Commit Analyzer")
        print("=" * 40)

        # Test commit data
        test_commit = {
            "id": "abc123456789",
            "short_id": "abc12345",
            "message": "fix: resolve state update loop in useEffect hook",
            "diff": """--- src/components/Timer.tsx
+++ src/components/Timer.tsx
@@ -15,7 +15,7 @@ export function Timer() {
   useEffect(() => {
-    setValue(input)
+    setValue(prevValue => input)
   }, [input])
   
   return <div>{value}</div>""",
            "files_changed": [
                {"path": "src/components/Timer.tsx", "change_type": "modified"}
            ],
            "stats": {"additions": 1, "deletions": 1, "files_changed": 1},
            "commit_type": "bugfix",
        }

        # Initialize analyzer (requires API key)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not set, skipping test")
            return

        analyzer = CommitAnalyzer(api_key=api_key)

        # Test analysis
        result = await analyzer.analyze_commit(test_commit)

        if result:
            print(f"✅ Analysis successful:")
            print(f"  Label: {result['label']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Reasoning: {result['reasoning']}")
        else:
            print("❌ Analysis failed")

        await analyzer.cleanup()

    # Run test
    asyncio.run(test_analyzer())
