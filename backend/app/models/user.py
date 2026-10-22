from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    resumes = relationship("Resume", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("JobDescription", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("MatchAnalysis", back_populates="owner", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="owner", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="owner", cascade="all, delete-orphan")
