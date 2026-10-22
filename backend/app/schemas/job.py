from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=20)
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    location: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    location: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    location: Optional[str] = None
    is_sample: bool = False
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
