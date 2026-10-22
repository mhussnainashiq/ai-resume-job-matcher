from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MatchRequest(BaseModel):
    resume_id: int
    job_id: int
    method: str = Field(default="hybrid", pattern="^(tfidf|semantic|hybrid)$")

class ComponentScores(BaseModel):
    required_skill_coverage: float = 0.0
    preferred_skill_coverage: float = 0.0
    semantic_similarity: float = 0.0
    experience_relevance: float = 0.0
    project_relevance: float = 0.0

class MatchAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    overall_score: float
    component_scores: Dict[str, float]
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    strengths: List[str] = []
    suggestions: List[str] = []
    evidence: List[str] = []
    matching_method: str
    created_at: datetime
    job_title: Optional[str] = None
    job_company: Optional[str] = None

    class Config:
        from_attributes = True

class SkillGapResponse(BaseModel):
    demonstrated_skills: List[str] = []
    missing_required: List[str] = []
    missing_preferred: List[str] = []
    transferable_skills: List[str] = []
    learning_priorities: List[str] = []

class RecommendationItem(BaseModel):
    job_id: int
    title: str
    company: str
    overall_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    explanation: str
    is_sample: bool = False

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total: int
