from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.services.job_service import seed_sample_jobs
from app.api import auth, resumes, jobs, matching, applications, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    db = SessionLocal()
    try:
        seed_sample_jobs(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Resume Analysis and Job Matching System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(applications.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health():
    from app.ml.matcher import is_semantic_available
    return {
        "status": "ok",
        "semantic_model_available": is_semantic_available(),
    }
