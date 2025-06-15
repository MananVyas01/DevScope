"""GitHub integration endpoints."""

import httpx
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.models.database import get_db
from app.models.models import User
from app.schemas.schemas import GitHubRepo, GitHubCommit, GitHubStats
from app.config import settings

router = APIRouter()


@router.get("/repos", response_model=List[GitHubRepo])
async def get_github_repos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's GitHub repositories."""
    if not current_user.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found. Please link your GitHub account.",
        )

    async with httpx.AsyncClient() as client:
        # Get user repos
        headers = {}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        response = await client.get(
            f"https://api.github.com/users/{current_user.github_username}/repos",
            headers=headers,
            params={"type": "owner", "sort": "updated", "per_page": 50},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch GitHub repositories",
            )

        repos_data = response.json()

        repos = []
        for repo_data in repos_data:
            repo = GitHubRepo(
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                description=repo_data.get("description"),
                html_url=repo_data["html_url"],
                clone_url=repo_data["clone_url"],
                language=repo_data.get("language"),
                stargazers_count=repo_data["stargazers_count"],
                forks_count=repo_data["forks_count"],
                updated_at=datetime.fromisoformat(
                    repo_data["updated_at"].replace("Z", "+00:00")
                ),
            )
            repos.append(repo)

        return repos


@router.get("/commits/{repo_name}")
async def get_github_commits(
    repo_name: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get commits from a specific repository."""
    if not current_user.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found. Please link your GitHub account.",
        )

    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    async with httpx.AsyncClient() as client:
        headers = {}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        # Get commits
        response = await client.get(
            f"https://api.github.com/repos/{current_user.github_username}/{repo_name}/commits",
            headers=headers,
            params={
                "author": current_user.github_username,
                "since": since_date,
                "per_page": 100,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch commits",
            )

        commits_data = response.json()
        commits = []

        for commit_data in commits_data:
            # Get detailed commit info for stats
            commit_detail_response = await client.get(
                f"https://api.github.com/repos/{current_user.github_username}/{repo_name}/commits/{commit_data['sha']}",
                headers=headers,
            )

            if commit_detail_response.status_code == 200:
                detail_data = commit_detail_response.json()

                commit = GitHubCommit(
                    sha=commit_data["sha"],
                    message=commit_data["commit"]["message"],
                    author=commit_data["commit"]["author"]["name"],
                    date=datetime.fromisoformat(
                        commit_data["commit"]["author"]["date"].replace("Z", "+00:00")
                    ),
                    additions=detail_data["stats"]["additions"],
                    deletions=detail_data["stats"]["deletions"],
                    files_changed=len(detail_data["files"]),
                )
                commits.append(commit)

        return {
            "repository": repo_name,
            "commits": commits,
            "total_commits": len(commits),
            "date_range": {"since": since_date, "until": datetime.now().isoformat()},
        }


@router.get("/stats", response_model=GitHubStats)
async def get_github_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get GitHub statistics for the user."""
    if not current_user.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found. Please link your GitHub account.",
        )

    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    async with httpx.AsyncClient() as client:
        headers = {}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        # Get user repos
        repos_response = await client.get(
            f"https://api.github.com/users/{current_user.github_username}/repos",
            headers=headers,
            params={"type": "owner", "per_page": 100},
        )

        if repos_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch GitHub repositories",
            )

        repos = repos_response.json()
        total_repos = len(repos)

        # Collect languages
        languages = {}
        all_commits = []
        total_commits = 0

        # Process each repository
        for repo in repos[:10]:  # Limit to 10 repos to avoid rate limiting
            repo_name = repo["name"]

            # Get commits for this repo
            commits_response = await client.get(
                f"https://api.github.com/repos/{current_user.github_username}/{repo_name}/commits",
                headers=headers,
                params={
                    "author": current_user.github_username,
                    "since": since_date,
                    "per_page": 50,
                },
            )

            if commits_response.status_code == 200:
                repo_commits = commits_response.json()
                total_commits += len(repo_commits)

                # Add recent commits to the list (limit to 5 per repo)
                for commit_data in repo_commits[:5]:
                    commit = GitHubCommit(
                        sha=commit_data["sha"],
                        message=commit_data["commit"]["message"],
                        author=commit_data["commit"]["author"]["name"],
                        date=datetime.fromisoformat(
                            commit_data["commit"]["author"]["date"].replace(
                                "Z", "+00:00"
                            )
                        ),
                        additions=0,  # Would need additional API call for detailed stats
                        deletions=0,
                        files_changed=0,
                    )
                    all_commits.append(commit)

            # Count language
            if repo.get("language"):
                language = repo["language"]
                languages[language] = languages.get(language, 0) + 1

        # Sort commits by date (most recent first)
        all_commits.sort(key=lambda x: x.date, reverse=True)
        recent_commits = all_commits[:10]  # Get 10 most recent commits

        # Calculate contribution streak (simplified)
        contribution_streak = 0
        if recent_commits:
            last_commit_date = recent_commits[0].date.date()
            current_date = datetime.now().date()

            # Simple streak calculation - count consecutive days with commits
            streak_date = current_date
            for commit in recent_commits:
                commit_date = commit.date.date()
                if (streak_date - commit_date).days <= 1:
                    if (
                        commit_date == streak_date
                        or commit_date == streak_date - timedelta(days=1)
                    ):
                        contribution_streak += 1
                        streak_date = commit_date
                else:
                    break

        return GitHubStats(
            total_commits=total_commits,
            total_repos=total_repos,
            languages=languages,
            recent_commits=recent_commits,
            contribution_streak=contribution_streak,
        )


@router.post("/sync-activity")
async def sync_github_activity(
    repo_name: str,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync GitHub activity as DevScope activities."""
    if not current_user.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub username not found. Please link your GitHub account.",
        )

    # Get commits from the specified repo
    commits_data = await get_github_commits(repo_name, days, current_user, db)
    commits = commits_data["commits"]

    # Import Activity model here to avoid circular imports
    from app.models.models import Activity, Project
    from sqlalchemy.future import select

    # Find or create project for this repo
    project_stmt = select(Project).where(
        Project.user_id == current_user.id,
        Project.github_repo == f"{current_user.github_username}/{repo_name}",
    )
    project = (await db.execute(project_stmt)).scalar_one_or_none()

    if not project:
        # Create new project
        project = Project(
            user_id=current_user.id,
            name=repo_name,
            description=f"GitHub repository: {repo_name}",
            github_repo=f"{current_user.github_username}/{repo_name}",
            color="#4F46E5",  # Default blue color
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

    # Create activities for commits
    activities_created = 0

    for commit in commits:
        # Check if activity already exists for this commit
        activity_stmt = select(Activity).where(
            Activity.user_id == current_user.id,
            Activity.description.contains(
                commit.sha[:8]
            ),  # Check if commit SHA is in description
        )
        existing_activity = (await db.execute(activity_stmt)).scalar_one_or_none()

        if not existing_activity:
            # Estimate duration based on changes (rough heuristic)
            estimated_minutes = min(
                max((commit.additions + commit.deletions) // 10, 15), 120
            )

            activity = Activity(
                user_id=current_user.id,
                project_id=project.id,
                activity_type="coding",
                description=f"Commit: {commit.message[:100]} ({commit.sha[:8]})",
                duration_minutes=estimated_minutes,
                started_at=commit.date,
                ended_at=commit.date,
                tags=["github", "commit", repo_name],
            )
            db.add(activity)
            activities_created += 1

    await db.commit()

    return {
        "message": f"Synced {activities_created} activities from GitHub",
        "repository": repo_name,
        "activities_created": activities_created,
        "total_commits_processed": len(commits),
    }
