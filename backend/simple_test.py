"""Simple test server for DevScope API."""

from fastapi import FastAPI

app = FastAPI(title="DevScope API Test", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "DevScope API is running!", "status": "healthy"}


@app.get("/health")
async def health():
    return {"status": "healthy", "api": "DevScope Backend"}


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting DevScope API test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
