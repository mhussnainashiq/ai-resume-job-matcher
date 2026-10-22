from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    created_at: datetime
    message: str = "Resume uploaded successfully"

    class Config:
        from_attributes = True

class ParsedProfileResponse(BaseModel):
    id: int
    resume_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    completeness_score: float = 0.0
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    created_at: datetime
    profile: Optional[ParsedProfileResponse] = None

    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total: int
