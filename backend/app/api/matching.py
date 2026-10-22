from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analysis import MatchAnalysis
from app.schemas.analysis import (
    MatchRequest, MatchAnalysisResponse, SkillGapResponse,
    RecommendationResponse, RecommendationItem
)
from app.services.match_service import run_match, get_skill_gap, get_recommendations

router = APIRouter(prefix="/api/matching", tags=["Matching"])

@router.post("/analyze", response_model=MatchAnalysisResponse)
def analyze_match(
    body: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = run_match(db, current_user, body.resume_id, body.job_id, body.method)
    resp = MatchAnalysisResponse.model_validate(analysis)
    if analysis.job:
        resp.job_title = analysis.job.title
        resp.job_company = analysis.job.company
    return resp

@router.get("/skill-gap", response_model=SkillGapResponse)
def skill_gap(
    resume_id: int = Query(...),
    job_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_skill_gap(db, current_user, resume_id, job_id)

@router.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    resume_id: int = Query(...),
    limit: int = Query(10, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = get_recommendations(db, current_user, resume_id, limit)
    return RecommendationResponse(
        recommendations=[RecommendationItem(**i) for i in items],
        total=len(items),
    )

@router.get("/history", response_model=List[MatchAnalysisResponse])
def match_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(MatchAnalysis)
        .filter(MatchAnalysis.user_id == current_user.id)
        .order_by(MatchAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    results = []
    for a in analyses:
        resp = MatchAnalysisResponse.model_validate(a)
        if a.job:
            resp.job_title = a.job.title
            resp.job_company = a.job.company
        results.append(resp)
    return results
