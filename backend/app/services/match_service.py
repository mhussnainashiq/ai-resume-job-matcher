from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import MatchAnalysis
from app.models.user import User
from app.ml.matcher import compute_match, skill_gap_analysis, is_semantic_available
from app.services.resume_service import get_resume_or_404
from app.services.job_service import get_job_or_404

def run_match(db: Session, user: User, resume_id: int, job_id: int, method: str = "hybrid") -> MatchAnalysis:
    resume = get_resume_or_404(db, resume_id, user.id)
    job = get_job_or_404(db, job_id, user.id)
    profile = resume.profile
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume has not been parsed yet")

    result = compute_match(
        resume_text=resume.raw_text or "",
        resume_skills=profile.skills or [],
        experience=profile.experience or [],
        projects=profile.projects or [],
        job_description=job.description,
        required_skills=job.required_skills or [],
        preferred_skills=job.preferred_skills or [],
        method=method,
    )

    analysis = MatchAnalysis(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id,
        overall_score=result["overall_score"],
        component_scores=result["component_scores"],
        matched_required_skills=result["matched_required_skills"],
        missing_required_skills=result["missing_required_skills"],
        matched_preferred_skills=result["matched_preferred_skills"],
        missing_preferred_skills=result["missing_preferred_skills"],
        strengths=result["strengths"],
        suggestions=result["suggestions"],
        evidence=result["evidence"],
        matching_method=result["matching_method"],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def get_skill_gap(db: Session, user: User, resume_id: int, job_id: int) -> dict:
    resume = get_resume_or_404(db, resume_id, user.id)
    job = get_job_or_404(db, job_id, user.id)
    profile = resume.profile
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume not parsed")
    return skill_gap_analysis(
        profile.skills or [],
        job.required_skills or [],
        job.preferred_skills or [],
    )

def get_recommendations(db: Session, user: User, resume_id: int, limit: int = 10) -> List[dict]:
    resume = get_resume_or_404(db, resume_id, user.id)
    profile = resume.profile
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume not parsed")

    jobs = db.query(JobDescription).filter(
        (JobDescription.user_id == user.id) | (JobDescription.is_sample == True)
    ).all()

    results = []
    for job in jobs:
        result = compute_match(
            resume_text=resume.raw_text or "",
            resume_skills=profile.skills or [],
            experience=profile.experience or [],
            projects=profile.projects or [],
            job_description=job.description,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
            method="hybrid",
        )
        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "overall_score": result["overall_score"],
            "matched_skills": result["matched_required_skills"] + result["matched_preferred_skills"],
            "missing_skills": result["missing_required_skills"],
            "explanation": "; ".join(result["strengths"][:2]) if result["strengths"] else "Compatibility score based on skills and text similarity",
            "is_sample": job.is_sample,
        })
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results[:limit]
