from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import logging
from dotenv import load_dotenv
from git_coach import GitCoach
from typing import List, Optional

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DevScope AI Engine",
    description="AI-powered backend services for DevScope",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:1420",
        "http://localhost:8000",
    ],  # Frontend, Desktop, and Backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalysisRequest(BaseModel):
    repo_path: Optional[str] = "."
    hours_back: Optional[int] = 24


class InsightResponse(BaseModel):
    summary: str
    suggestions: List[str]
    productivity_score: int
    tags: List[str]


@app.get("/")
async def root():
    return {
        "message": "DevScope AI Engine is running!",
        "groq_available": bool(os.getenv("GROQ_API_KEY")),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-engine",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/analyze", response_model=InsightResponse)
async def analyze_code(request: AnalysisRequest):
    """Generate AI insights from git repository analysis"""
    try:
        # Initialize GitCoach with GROQ API
        coach = GitCoach(
            repo_path=request.repo_path,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            prefer_groq=True,
        )

        # Get git analysis
        git_data = coach.get_git_data(hours_back=request.hours_back)

        if not git_data or git_data.get("total_commits", 0) == 0:
            return InsightResponse(
                summary="No recent git activity found in the specified timeframe.",
                suggestions=[
                    "Start coding to get AI insights!",
                    "Make some commits to see analysis.",
                ],
                productivity_score=0,
                tags=["no-activity"],
            )

        # Generate AI insights
        insights = coach.generate_insights(git_data)

        return InsightResponse(
            summary=insights.get("summary", "Analysis completed"),
            suggestions=insights.get("suggestions", []),
            productivity_score=insights.get("productivity_score", 7),
            tags=insights.get("tags", ["general"]),
        )

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/insights/quick")
async def quick_insights():
    """Get quick AI insights without detailed analysis"""
    try:
        coach = GitCoach(groq_api_key=os.getenv("GROQ_API_KEY"))

        # Get basic analysis
        insights = coach.generate_quick_insights()

        return {
            "summary": insights.get("summary", "Keep up the great work!"),
            "suggestions": insights.get(
                "suggestions",
                [
                    "Focus on consistent commits",
                    "Document your code changes",
                    "Consider code reviews",
                ],
            ),
            "productivity_score": insights.get("productivity_score", 7),
            "tags": insights.get("tags", ["general"]),
        }

    except Exception as e:
        logger.error(f"Quick insights failed: {str(e)}")
        return {
            "summary": "AI insights are being prepared for you.",
            "suggestions": [
                "Continue your development workflow",
                "Make regular commits to track progress",
                "Use descriptive commit messages",
            ],
            "productivity_score": 7,
            "tags": ["general"],
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
