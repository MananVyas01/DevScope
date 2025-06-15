"""
Database Client for DevScope AI Activity Analyzer

This module handles communication with the DevScope backend API to store
analysis results in the PostgreSQL database.
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
import aiofiles


class BackendAPIClient:
    """Client for communicating with DevScope backend API."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the backend API client.

        Args:
            base_url: Base URL of the backend API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = None

        # Offline storage
        self.offline_file = os.getenv(
            "OFFLINE_CACHE_FILE", "./cache/offline_analysis.json"
        )
        self.retry_queue = []

        print(f"💾 BackendAPIClient initialized with base URL: {base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if not self.session:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "DevScope-AI-Engine/1.0",
            }

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)

        return self.session

    async def store_analysis(self, commit_data: Dict) -> bool:
        """
        Store analysis result in the backend database.

        Args:
            commit_data: Dictionary containing commit and analysis data

        Returns:
            True if successfully stored, False otherwise
        """
        try:
            # Prepare the activity data for the backend
            activity_data = self._prepare_activity_data(commit_data)

            # Try to send to backend
            if await self._send_to_backend(activity_data):
                return True
            else:
                # Store offline for later retry
                await self._store_offline(activity_data)
                return False

        except Exception as e:
            print(f"  ❌ Error storing analysis: {e}")
            # Store offline as fallback
            try:
                activity_data = self._prepare_activity_data(commit_data)
                await self._store_offline(activity_data)
            except:
                pass
            return False

    def _prepare_activity_data(self, commit_data: Dict) -> Dict:
        """
        Prepare commit data for the backend API format.

        Args:
            commit_data: Raw commit data with analysis

        Returns:
            Formatted data for backend API
        """
        analysis = commit_data.get("analysis", {})

        # Map AI classification to backend activity types
        activity_type_mapping = {
            "High Focus": "coding",
            "Feature Development": "coding",
            "Bug Fixing": "debugging",
            "Refactoring": "refactoring",
            "Testing": "testing",
            "Documentation": "documentation",
            "Code Review": "review",
            "Research Spike": "research",
            "Setup/Configuration": "setup",
            "Distracted": "other",
        }

        ai_label = analysis.get("label", "other")
        activity_type = activity_type_mapping.get(ai_label, "other")

        # Extract timing information
        commit_time = commit_data.get("timestamp", datetime.now().isoformat())

        # Estimate duration based on changes (rough heuristic)
        stats = commit_data.get("stats", {})
        changes_count = stats.get("additions", 0) + stats.get("deletions", 0)

        # Rough estimate: 1 line change = 30 seconds of work, capped between 5-120 minutes
        estimated_duration = max(5, min(120, changes_count * 0.5))

        # Prepare tags
        tags = [
            "ai-analyzed",
            f'confidence-{int(analysis.get("confidence", 0) * 100)}',
            ai_label.lower().replace(" ", "-"),
            commit_data.get("commit_type", "unknown"),
        ]

        # Add file type tags
        file_extensions = set()
        for file_change in commit_data.get("files_changed", []):
            path = file_change.get("path", "")
            if "." in path:
                ext = path.split(".")[-1].lower()
                file_extensions.add(ext)

        tags.extend(
            [f"ext-{ext}" for ext in list(file_extensions)[:5]]
        )  # Limit to 5 extensions

        return {
            "activity_type": activity_type,
            "description": f"AI Analysis: {analysis.get('reasoning', 'Automated commit analysis')}",
            "duration_minutes": int(estimated_duration),
            "start_time": commit_time,
            "tags": tags,
            "metadata": {
                "commit_id": commit_data.get("id"),
                "commit_message": commit_data.get("message", ""),
                "ai_classification": analysis.get("label"),
                "ai_confidence": analysis.get("confidence"),
                "ai_reasoning": analysis.get("reasoning"),
                "ai_indicators": analysis.get("indicators", []),
                "files_changed": len(commit_data.get("files_changed", [])),
                "lines_added": stats.get("additions", 0),
                "lines_deleted": stats.get("deletions", 0),
                "branch": commit_data.get("branch", "unknown"),
                "author": commit_data.get("author", {}),
                "is_merge": commit_data.get("is_merge", False),
            },
        }

    async def _send_to_backend(self, activity_data: Dict) -> bool:
        """
        Send activity data to the backend API.

        Args:
            activity_data: Formatted activity data

        Returns:
            True if successful, False otherwise
        """
        try:
            session = await self._get_session()

            # Endpoint for creating activities
            url = f"{self.base_url}/timer/session/complete"

            async with session.post(url, json=activity_data) as response:
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    print(f"  ✅ Stored in backend: {result.get('id', 'unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"  ⚠️ Backend error {response.status}: {error_text[:100]}")
                    return False

        except aiohttp.ClientError as e:
            print(f"  ⚠️ Network error: {e}")
            return False
        except Exception as e:
            print(f"  ⚠️ Unexpected error sending to backend: {e}")
            return False

    async def _store_offline(self, activity_data: Dict):
        """
        Store activity data offline for later retry.

        Args:
            activity_data: Activity data to store offline
        """
        try:
            # Add timestamp for retry tracking
            offline_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": activity_data,
                "retry_count": 0,
            }

            # Load existing offline data
            offline_data = []
            if os.path.exists(self.offline_file):
                try:
                    async with aiofiles.open(self.offline_file, "r") as f:
                        content = await f.read()
                        offline_data = json.loads(content)
                except:
                    pass  # Start fresh if corrupted

            # Add new entry
            offline_data.append(offline_entry)

            # Save back to file
            os.makedirs(os.path.dirname(self.offline_file), exist_ok=True)
            async with aiofiles.open(self.offline_file, "w") as f:
                await f.write(json.dumps(offline_data, indent=2))

            print(f"  💾 Stored offline for later retry")

        except Exception as e:
            print(f"  ⚠️ Error storing offline data: {e}")

    async def retry_offline_data(self) -> Dict[str, int]:
        """
        Retry sending offline stored data to the backend.

        Returns:
            Dictionary with retry statistics
        """
        if not os.path.exists(self.offline_file):
            return {"attempted": 0, "successful": 0, "failed": 0}

        try:
            # Load offline data
            async with aiofiles.open(self.offline_file, "r") as f:
                content = await f.read()
                offline_data = json.loads(content)

            if not offline_data:
                return {"attempted": 0, "successful": 0, "failed": 0}

            print(f"📡 Retrying {len(offline_data)} offline entries...")

            successful = []
            failed = []

            for entry in offline_data:
                activity_data = entry["data"]
                retry_count = entry.get("retry_count", 0)

                # Skip entries that have failed too many times
                if retry_count >= 5:
                    failed.append(entry)
                    continue

                # Try to send
                if await self._send_to_backend(activity_data):
                    successful.append(entry)
                else:
                    # Increment retry count
                    entry["retry_count"] = retry_count + 1
                    failed.append(entry)

            # Save remaining failed entries
            if failed:
                async with aiofiles.open(self.offline_file, "w") as f:
                    await f.write(json.dumps(failed, indent=2))
            else:
                # Remove the file if all entries were successful
                os.remove(self.offline_file)

            stats = {
                "attempted": len(offline_data),
                "successful": len(successful),
                "failed": len(failed),
            }

            print(
                f"📊 Retry results: {stats['successful']}/{stats['attempted']} successful"
            )
            return stats

        except Exception as e:
            print(f"❌ Error during offline retry: {e}")
            return {"attempted": 0, "successful": 0, "failed": 0}

    async def health_check(self) -> bool:
        """
        Check if the backend API is available.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            session = await self._get_session()

            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(
                        f"✅ Backend health check passed: {health_data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    print(f"⚠️ Backend health check failed: {response.status}")
                    return False

        except Exception as e:
            print(f"⚠️ Backend health check error: {e}")
            return False

    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None


# Test function for development
if __name__ == "__main__":

    async def test_client():
        print("💾 Testing Backend API Client")
        print("=" * 40)

        # Test data
        test_commit_data = {
            "id": "test123456789",
            "message": "fix: resolve timer state issue",
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "label": "Bug Fixing",
                "confidence": 0.85,
                "reasoning": "Fix keyword in message, targeted changes in state management",
            },
            "stats": {"additions": 5, "deletions": 2, "files_changed": 1},
            "files_changed": [{"path": "src/timer.js", "change_type": "modified"}],
            "commit_type": "bugfix",
            "branch": "main",
            "author": {"name": "Test User", "email": "test@example.com"},
        }

        # Initialize client
        client = BackendAPIClient(
            base_url=os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")
        )

        # Test health check
        is_healthy = await client.health_check()
        print(f"Backend healthy: {is_healthy}")

        # Test data preparation
        activity_data = client._prepare_activity_data(test_commit_data)
        print(f"✅ Activity data prepared:")
        print(f"  Type: {activity_data['activity_type']}")
        print(f"  Duration: {activity_data['duration_minutes']} minutes")
        print(f"  Tags: {activity_data['tags'][:3]}...")

        # Test storage (will go offline if backend not available)
        success = await client.store_analysis(test_commit_data)
        print(f"Storage result: {success}")

        await client.cleanup()

    # Run test
    asyncio.run(test_client())
