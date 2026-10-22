from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class SavedJobCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None

class SavedJobResponse(BaseModel):
    id: int
    job_id: int
    notes: Optional[str] = None
    created_at: datetime
    job_title: Optional[str] = None
    job_company: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    job_id: int
    status: str = Field(default="Applied", pattern="^(Applied|Interview|Offer|Rejected|Withdrawn)$")
    applied_date: Optional[date] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Applied|Interview|Offer|Rejected|Withdrawn)$")
    applied_date: Optional[date] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    applied_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job_title: Optional[str] = None
    job_company: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_resumes: int = 0
    total_jobs: int = 0
    total_analyses: int = 0
    average_compatibility: float = 0.0
    top_matched_skills: List[dict] = []
    common_skill_gaps: List[dict] = []
    recent_analyses: List[dict] = []
    application_stats: dict = {}
    saved_jobs_count: int = 0
