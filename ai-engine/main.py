from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

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
    ],  # Frontend and Desktop
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "DevScope AI Engine is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-engine"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
