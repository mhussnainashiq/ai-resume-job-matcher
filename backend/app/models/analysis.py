from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class MatchAnalysis(Base):
    __tablename__ = "match_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    component_scores = Column(JSON, default=dict)
    matched_required_skills = Column(JSON, default=list)
    missing_required_skills = Column(JSON, default=list)
    matched_preferred_skills = Column(JSON, default=list)
    missing_preferred_skills = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    matching_method = Column(String(50), default="tfidf")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
    job = relationship("JobDescription", back_populates="analyses")
