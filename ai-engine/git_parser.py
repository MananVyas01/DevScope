"""
Git Log Parser for DevScope AI Activity Analyzer

This module handles parsing Git commit logs, extracting diffs, and preparing
commit data for AI analysis.
"""

import os
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import git
from git import Repo


class GitLogParser:
    """Parses Git logs and extracts commit information with diffs."""
    
    def __init__(self, repo_path: str = "../", hours_back: int = 24):
        """
        Initialize the Git log parser.
        
        Args:
            repo_path: Path to the Git repository
            hours_back: How many hours back to analyze commits
        """
        self.repo_path = os.path.abspath(repo_path)
        self.hours_back = hours_back
        self.repo = None
        
        try:
            self.repo = Repo(self.repo_path)
            if self.repo.bare:
                raise git.InvalidGitRepositoryError("Repository is bare")
        except (git.InvalidGitRepositoryError, git.NoSuchPathError) as e:
            print(f"⚠️ Git repository error: {e}")
            self.repo = None
    
    def get_recent_commits(self) -> List[Dict]:
        """
        Get commits from the specified time period.
        
        Returns:
            List of commit dictionaries with metadata and diffs
        """
        if not self.repo:
            print("❌ No valid Git repository found")
            return []
        
        # Calculate the time threshold
        since_time = datetime.now() - timedelta(hours=self.hours_back)
        
        commits = []
        try:
            # Get commits since the specified time
            commit_iter = self.repo.iter_commits(
                since=since_time,
                max_count=50  # Limit to prevent excessive API calls
            )
            
            for commit in commit_iter:
                commit_data = self._extract_commit_data(commit)
                if commit_data:
                    commits.append(commit_data)
            
            print(f"📋 Found {len(commits)} commits in the last {self.hours_back} hours")
            return commits
            
        except Exception as e:
            print(f"❌ Error parsing commits: {e}")
            return []
    
    def _extract_commit_data(self, commit) -> Optional[Dict]:
        """
        Extract comprehensive data from a single commit.
        
        Args:
            commit: GitPython commit object
            
        Returns:
            Dictionary with commit data or None if extraction fails
        """
        try:
            # Basic commit information
            commit_data = {
                'id': str(commit.hexsha),
                'short_id': str(commit.hexsha)[:8],
                'message': commit.message.strip(),
                'author': {
                    'name': commit.author.name,
                    'email': commit.author.email
                },
                'timestamp': commit.committed_datetime.isoformat(),
                'branch': self._get_commit_branch(commit),
                'files_changed': [],
                'diff': '',
                'stats': {
                    'additions': 0,
                    'deletions': 0,
                    'files_changed': 0
                }
            }
            
            # Get diff information
            if commit.parents:
                # Compare with first parent (main diff)
                parent = commit.parents[0]
                diff = parent.diff(commit)
                
                commit_data['diff'] = self._format_diff(diff)
                commit_data['files_changed'] = self._extract_file_changes(diff)
                commit_data['stats'] = self._calculate_diff_stats(diff)
            else:
                # First commit - compare with empty tree
                diff = commit.diff(git.NULL_TREE)
                commit_data['diff'] = self._format_diff(diff)
                commit_data['files_changed'] = self._extract_file_changes(diff)
                commit_data['stats'] = self._calculate_diff_stats(diff)
            
            # Classify commit type based on message
            commit_data['commit_type'] = self._classify_commit_type(commit.message)
            
            # Check if this might be a merge commit
            commit_data['is_merge'] = len(commit.parents) > 1
            
            return commit_data
            
        except Exception as e:
            print(f"⚠️ Error extracting commit data for {commit.hexsha[:8]}: {e}")
            return None
    
    def _get_commit_branch(self, commit) -> str:
        """Get the branch name for a commit."""
        try:
            # Try to find which branch contains this commit
            branches = [branch.name for branch in self.repo.branches if commit in branch.commit.iter_parents()]
            if branches:
                return branches[0]
            
            # Fallback to current branch
            if self.repo.active_branch:
                return self.repo.active_branch.name
                
            return "unknown"
        except:
            return "unknown"
    
    def _format_diff(self, diff) -> str:
        """
        Format diff information for AI analysis.
        
        Args:
            diff: GitPython diff object
            
        Returns:
            Formatted diff string
        """
        diff_text = []
        
        for diff_item in diff:
            if diff_item.a_path:
                file_path = diff_item.a_path
            elif diff_item.b_path:
                file_path = diff_item.b_path
            else:
                file_path = "unknown"
            
            # Add file header
            if diff_item.new_file:
                diff_text.append(f"--- /dev/null")
                diff_text.append(f"+++ {file_path}")
            elif diff_item.deleted_file:
                diff_text.append(f"--- {file_path}")
                diff_text.append(f"+++ /dev/null")
            else:
                diff_text.append(f"--- {file_path}")
                diff_text.append(f"+++ {file_path}")
            
            # Add the actual diff content (limit to prevent token overflow)
            try:
                if hasattr(diff_item, 'diff') and diff_item.diff:
                    diff_content = diff_item.diff.decode('utf-8', errors='ignore')
                    # Limit diff size to prevent OpenAI token overflow
                    if len(diff_content) > 2000:
                        diff_content = diff_content[:2000] + "\n... (truncated)"
                    diff_text.append(diff_content)
            except Exception as e:
                diff_text.append(f"(Binary file or diff error: {e})")
        
        return "\n".join(diff_text)
    
    def _extract_file_changes(self, diff) -> List[Dict]:
        """Extract information about changed files."""
        files = []
        
        for diff_item in diff:
            file_info = {
                'path': diff_item.a_path or diff_item.b_path or 'unknown',
                'change_type': 'modified'
            }
            
            if diff_item.new_file:
                file_info['change_type'] = 'added'
            elif diff_item.deleted_file:
                file_info['change_type'] = 'deleted'
            elif diff_item.renamed_file:
                file_info['change_type'] = 'renamed'
                file_info['old_path'] = diff_item.rename_from
            
            files.append(file_info)
        
        return files
    
    def _calculate_diff_stats(self, diff) -> Dict:
        """Calculate statistics about the diff."""
        stats = {
            'additions': 0,
            'deletions': 0,
            'files_changed': len(diff)
        }
        
        for diff_item in diff:
            try:
                if hasattr(diff_item, 'diff') and diff_item.diff:
                    diff_content = diff_item.diff.decode('utf-8', errors='ignore')
                    lines = diff_content.split('\n')
                    
                    for line in lines:
                        if line.startswith('+') and not line.startswith('+++'):
                            stats['additions'] += 1
                        elif line.startswith('-') and not line.startswith('---'):
                            stats['deletions'] += 1
            except:
                continue
        
        return stats
    
    def _classify_commit_type(self, message: str) -> str:
        """
        Basic classification of commit type based on message.
        
        Args:
            message: Commit message
            
        Returns:
            Commit type category
        """
        message_lower = message.lower()
        
        # Common commit message patterns
        if any(word in message_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'bugfix'
        elif any(word in message_lower for word in ['feat', 'feature', 'add', 'implement']):
            return 'feature'
        elif any(word in message_lower for word in ['refactor', 'restructure', 'reorganize']):
            return 'refactor'
        elif any(word in message_lower for word in ['test', 'spec', 'testing']):
            return 'test'
        elif any(word in message_lower for word in ['doc', 'readme', 'comment']):
            return 'documentation'
        elif any(word in message_lower for word in ['style', 'format', 'lint']):
            return 'style'
        elif any(word in message_lower for word in ['merge', 'pull request', 'pr']):
            return 'merge'
        elif any(word in message_lower for word in ['initial', 'init', 'setup']):
            return 'initial'
        else:
            return 'other'
    
    def get_repository_info(self) -> Dict:
        """Get basic repository information."""
        if not self.repo:
            return {'error': 'No repository available'}
        
        try:
            return {
                'path': self.repo_path,
                'current_branch': self.repo.active_branch.name if self.repo.active_branch else 'detached',
                'total_commits': len(list(self.repo.iter_commits())),
                'remotes': [remote.name for remote in self.repo.remotes],
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': len(self.repo.untracked_files)
            }
        except Exception as e:
            return {'error': f'Error getting repository info: {e}'}


# Test function for development
if __name__ == "__main__":
    parser = GitLogParser()
    
    print("🔍 Testing Git Log Parser")
    print("=" * 40)
    
    # Test repository info
    repo_info = parser.get_repository_info()
    print(f"Repository Info: {repo_info}")
    
    # Test commit parsing
    commits = parser.get_recent_commits()
    print(f"\nFound {len(commits)} recent commits")
    
    for i, commit in enumerate(commits[:3]):  # Show first 3 commits
        print(f"\nCommit {i+1}:")
        print(f"  ID: {commit['short_id']}")
        print(f"  Message: {commit['message'][:60]}...")
        print(f"  Type: {commit['commit_type']}")
        print(f"  Files changed: {commit['stats']['files_changed']}")
        print(f"  +{commit['stats']['additions']} -{commit['stats']['deletions']}")
