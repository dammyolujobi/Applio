from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import SlowApi, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from router import user, aggregator
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Applio Job Aggregator",
    description="A comprehensive job aggregation platform with advanced filtering, user management, and multi-source scraping",
    version="2.0.0"
)

# Rate limiter setup
limiter = SlowApi(request_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# CORS Configuration - Fixed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with rate limiting
app.include_router(user.router)
app.include_router(aggregator.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Applio Job Aggregator API",
        "version": "2.0.0",
        "features": [
            "User authentication with JWT tokens",
            "Job aggregation from multiple sources",
            "Advanced filtering and sorting",
            "Pagination support",
            "Job caching for performance",
            "Save/favorite jobs",
            "Job alerts",
            "Application tracking",
            "Search history",
            "User activity tracking"
        ],
        "endpoints": {
            "auth": "/users/register, /users/login, /users/refresh-token",
            "profile": "/users/me, /users/change-password",
            "jobs": "/aggregate, /jobs/{job_id}",
            "saved_jobs": "/users/saved-jobs",
            "alerts": "/users/alerts",
            "applications": "/users/applications",
            "history": "/users/search-history"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
