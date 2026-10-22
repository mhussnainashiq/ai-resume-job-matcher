from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import MatchAnalysis
from app.models.application import SavedJob, JobApplication
from app.schemas.application import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_jobs = db.query(JobDescription).filter(
        (JobDescription.user_id == current_user.id) | (JobDescription.is_sample == True)
    ).count()
    analyses = db.query(MatchAnalysis).filter(MatchAnalysis.user_id == current_user.id).all()
    total_analyses = len(analyses)
    avg_score = round(sum(a.overall_score for a in analyses) / total_analyses, 1) if analyses else 0.0

    # Top matched skills
    skill_counter = Counter()
    gap_counter = Counter()
    for a in analyses:
        for s in (a.matched_required_skills or []) + (a.matched_preferred_skills or []):
            skill_counter[s] += 1
        for s in (a.missing_required_skills or []):
            gap_counter[s] += 1
    top_matched = [{"skill": k, "count": v} for k, v in skill_counter.most_common(8)]
    common_gaps = [{"skill": k, "count": v} for k, v in gap_counter.most_common(8)]

    recent = []
    for a in sorted(analyses, key=lambda x: x.created_at, reverse=True)[:5]:
        job = db.query(JobDescription).get(a.job_id)
        recent.append({
            "id": a.id,
            "score": a.overall_score,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "",
            "method": a.matching_method,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })

    apps = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).all()
    status_counts = Counter(a.status for a in apps)
    app_stats = dict(status_counts)

    saved_count = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).count()

    return DashboardStats(
        total_resumes=total_resumes,
        total_jobs=total_jobs,
        total_analyses=total_analyses,
        average_compatibility=avg_score,
        top_matched_skills=top_matched,
        common_skill_gaps=common_gaps,
        recent_analyses=recent,
        application_stats=app_stats,
        saved_jobs_count=saved_count,
    )
