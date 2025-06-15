"""GitHub App webhook endpoints for real-time integration."""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any

import httpx
from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import get_db
from app.models.models import User, Project, Activity
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature."""
    if not settings.GITHUB_WEBHOOK_SECRET:
        logger.warning("GitHub webhook secret not configured")
        return True  # Allow in development mode

    if not signature_header:
        return False

    # GitHub sends signature as 'sha256=<hash>'
    try:
        hash_algorithm, github_signature = signature_header.split("=", 1)
    except ValueError:
        return False

    if hash_algorithm != "sha256":
        return False

    # Create HMAC hash of the payload
    expected_signature = hmac.new(
        key=settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Compare signatures using constant-time comparison
    return hmac.compare_digest(expected_signature, github_signature)


async def find_user_by_github_username(db: AsyncSession, github_username: str) -> User:
    """Find user by GitHub username."""
    stmt = select(User).where(User.github_username == github_username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def find_or_create_project(
    db: AsyncSession, user: User, repo_full_name: str, repo_name: str
) -> Project:
    """Find or create project for GitHub repository."""
    # Check if project exists
    stmt = select(Project).where(
        Project.user_id == user.id, Project.github_repo == repo_full_name
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        # Create new project
        project = Project(
            user_id=user.id,
            name=repo_name,
            description=f"GitHub repository: {repo_name}",
            github_repo=repo_full_name,
            color="#4F46E5",  # Default blue color
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

    return project


async def trigger_ai_analysis(
    repo_full_name: str, commit_sha: str, user_github_username: str
):
    """Trigger AI analysis for the commit (background task)."""
    try:
        # Call the AI analyzer service
        async with httpx.AsyncClient(timeout=30.0) as client:
            # This would typically call your AI analyzer microservice
            # For now, we'll just log the intent
            logger.info(
                f"Would trigger AI analysis for {repo_full_name}@{commit_sha} by {user_github_username}"
            )

            # If you have the AI analyzer running as a service, you could call it like:
            # response = await client.post(
            #     "http://ai-analyzer:8000/analyze",
            #     json={
            #         "repo": repo_full_name,
            #         "commit": commit_sha,
            #         "username": user_github_username
            #     }
            # )
    except Exception as e:
        logger.error(f"Failed to trigger AI analysis: {e}")


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub webhook events."""
    # Get headers
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256")

    # Get raw body for signature verification
    body = await request.body()

    # Verify signature
    if not verify_github_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature"
        )

    # Parse JSON payload
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload"
        )

    logger.info(f"Received GitHub webhook: {event_type}")

    # Handle different event types
    if event_type == "push":
        await handle_push_event(db, payload, background_tasks)
    elif event_type == "pull_request":
        await handle_pull_request_event(db, payload, background_tasks)
    elif event_type == "create":
        await handle_create_event(db, payload)
    elif event_type == "delete":
        await handle_delete_event(db, payload)
    else:
        logger.info(f"Unhandled event type: {event_type}")

    return {"status": "ok", "event": event_type}


async def handle_push_event(
    db: AsyncSession, payload: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Handle push events (commits)."""
    try:
        repo = payload.get("repository", {})
        commits = payload.get("commits", [])
        pusher = payload.get("pusher", {})

        repo_full_name = repo.get("full_name")
        repo_name = repo.get("name")
        pusher_username = pusher.get("name")

        if not repo_full_name or not pusher_username:
            logger.warning("Missing required data in push event")
            return

        # Find user
        user = await find_user_by_github_username(db, pusher_username)
        if not user:
            logger.info(f"User not found for GitHub username: {pusher_username}")
            return

        # Find or create project
        project = await find_or_create_project(db, user, repo_full_name, repo_name)

        # Process each commit
        for commit_data in commits:
            commit_sha = commit_data.get("id")
            commit_message = commit_data.get("message", "")
            commit_timestamp = commit_data.get("timestamp")
            author = commit_data.get("author", {})

            if not commit_sha or not commit_timestamp:
                continue

            # Parse timestamp
            try:
                commit_date = datetime.fromisoformat(
                    commit_timestamp.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                commit_date = datetime.now()

            # Estimate duration based on commit message and changes
            added_files = len(commit_data.get("added", []))
            modified_files = len(commit_data.get("modified", []))
            removed_files = len(commit_data.get("removed", []))
            total_changes = added_files + modified_files + removed_files

            # Rough heuristic for duration (5-60 minutes based on changes)
            estimated_duration = min(max(total_changes * 5, 5), 60)

            # Check if activity already exists
            stmt = select(Activity).where(
                Activity.user_id == user.id,
                Activity.description.contains(commit_sha[:8]),
            )
            result = await db.execute(stmt)
            existing_activity = result.scalar_one_or_none()

            if not existing_activity:
                # Create activity
                activity = Activity(
                    user_id=user.id,
                    project_id=project.id,
                    activity_type="coding",
                    description=f"Commit: {commit_message[:100]} ({commit_sha[:8]})",
                    duration_minutes=estimated_duration,
                    started_at=commit_date,
                    ended_at=commit_date,
                    tags=["github", "commit", repo_name],
                    metadata={
                        "commit_sha": commit_sha,
                        "repository": repo_full_name,
                        "files_added": added_files,
                        "files_modified": modified_files,
                        "files_removed": removed_files,
                        "author_email": author.get("email"),
                        "github_event": "push",
                    },
                )
                db.add(activity)

                # Trigger AI analysis in background
                background_tasks.add_task(
                    trigger_ai_analysis, repo_full_name, commit_sha, pusher_username
                )

        await db.commit()
        logger.info(f"Processed {len(commits)} commits for {repo_full_name}")

    except Exception as e:
        logger.error(f"Error handling push event: {e}")
        await db.rollback()


async def handle_pull_request_event(
    db: AsyncSession, payload: Dict[str, Any], background_tasks: BackgroundTasks
):
    """Handle pull request events."""
    try:
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})

        if action not in ["opened", "closed", "merged"]:
            return  # Only handle specific actions

        repo_full_name = repo.get("full_name")
        repo_name = repo.get("name")
        pr_author = pr.get("user", {}).get("login")
        pr_title = pr.get("title", "")
        pr_number = pr.get("number")

        if not repo_full_name or not pr_author:
            return

        # Find user
        user = await find_user_by_github_username(db, pr_author)
        if not user:
            return

        # Find or create project
        project = await find_or_create_project(db, user, repo_full_name, repo_name)

        # Estimate duration based on action
        duration_map = {
            "opened": 30,  # 30 minutes to create PR
            "closed": 5,  # 5 minutes to close PR
            "merged": 10,  # 10 minutes for merge activities
        }

        estimated_duration = duration_map.get(action, 15)

        # Create activity
        activity = Activity(
            user_id=user.id,
            project_id=project.id,
            activity_type="coding",
            description=f"PR {action}: {pr_title} (#{pr_number})",
            duration_minutes=estimated_duration,
            started_at=datetime.now(),
            ended_at=datetime.now(),
            tags=["github", "pull_request", repo_name, action],
            metadata={
                "pr_number": pr_number,
                "pr_action": action,
                "repository": repo_full_name,
                "github_event": "pull_request",
            },
        )
        db.add(activity)

        await db.commit()
        logger.info(f"Processed PR {action} for {repo_full_name}#{pr_number}")

    except Exception as e:
        logger.error(f"Error handling pull request event: {e}")
        await db.rollback()


async def handle_create_event(db: AsyncSession, payload: Dict[str, Any]):
    """Handle repository/branch creation events."""
    try:
        ref_type = payload.get("ref_type")  # "repository" or "branch"
        ref = payload.get("ref")  # branch name or None for repo
        repo = payload.get("repository", {})
        sender = payload.get("sender", {})

        repo_full_name = repo.get("full_name")
        repo_name = repo.get("name")
        sender_username = sender.get("login")

        if not repo_full_name or not sender_username:
            return

        # Find user
        user = await find_user_by_github_username(db, sender_username)
        if not user:
            return

        if ref_type == "repository":
            # New repository created - create project
            project = await find_or_create_project(db, user, repo_full_name, repo_name)

            activity = Activity(
                user_id=user.id,
                project_id=project.id,
                activity_type="planning",
                description=f"Created repository: {repo_name}",
                duration_minutes=15,
                started_at=datetime.now(),
                ended_at=datetime.now(),
                tags=["github", "repository", "create"],
                metadata={
                    "repository": repo_full_name,
                    "github_event": "create",
                    "ref_type": ref_type,
                },
            )
            db.add(activity)
            await db.commit()

        logger.info(f"Processed create event: {ref_type} for {repo_full_name}")

    except Exception as e:
        logger.error(f"Error handling create event: {e}")
        await db.rollback()


async def handle_delete_event(db: AsyncSession, payload: Dict[str, Any]):
    """Handle repository/branch deletion events."""
    try:
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        repo = payload.get("repository", {})
        sender = payload.get("sender", {})

        repo_full_name = repo.get("full_name")
        sender_username = sender.get("login")

        if not repo_full_name or not sender_username:
            return

        # Find user
        user = await find_user_by_github_username(db, sender_username)
        if not user:
            return

        # Log deletion event (we don't actually delete projects/activities)
        logger.info(
            f"GitHub {ref_type} deleted: {ref} in {repo_full_name} by {sender_username}"
        )

        # Optionally create an activity for branch deletions
        if ref_type == "branch" and ref != "main" and ref != "master":
            project = await find_or_create_project(
                db, user, repo_full_name, repo.get("name")
            )

            activity = Activity(
                user_id=user.id,
                project_id=project.id,
                activity_type="coding",
                description=f"Deleted branch: {ref}",
                duration_minutes=5,
                started_at=datetime.now(),
                ended_at=datetime.now(),
                tags=["github", "branch", "delete"],
                metadata={
                    "repository": repo_full_name,
                    "github_event": "delete",
                    "ref_type": ref_type,
                    "ref": ref,
                },
            )
            db.add(activity)
            await db.commit()

    except Exception as e:
        logger.error(f"Error handling delete event: {e}")
        await db.rollback()


@router.get("/webhook/status")
async def webhook_status():
    """Check webhook status and configuration."""
    return {
        "status": "active",
        "webhook_secret_configured": bool(settings.GITHUB_WEBHOOK_SECRET),
        "supported_events": ["push", "pull_request", "create", "delete"],
        "ai_analysis_enabled": True,
    }
