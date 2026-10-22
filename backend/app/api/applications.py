from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.application import SavedJob, JobApplication
from app.models.job import JobDescription
from app.schemas.application import (
    SavedJobCreate, SavedJobResponse, ApplicationCreate,
    ApplicationUpdate, ApplicationResponse
)
from app.services.job_service import get_job_or_404

router = APIRouter(prefix="/api/applications", tags=["Applications"])

@router.post("/saved", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    body: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(db, body.job_id, current_user.id)
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id, SavedJob.job_id == body.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")
    saved = SavedJob(user_id=current_user.id, job_id=body.job_id, notes=body.notes)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return SavedJobResponse(
        id=saved.id, job_id=saved.job_id, notes=saved.notes,
        created_at=saved.created_at, job_title=job.title, job_company=job.company
    )

@router.get("/saved", response_model=List[SavedJobResponse])
def list_saved(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(SavedJob).filter(SavedJob.user_id == current_user.id).all()
    results = []
    for s in items:
        job = db.query(JobDescription).get(s.job_id)
        results.append(SavedJobResponse(
            id=s.id, job_id=s.job_id, notes=s.notes, created_at=s.created_at,
            job_title=job.title if job else None, job_company=job.company if job else None
        ))
    return results

@router.delete("/saved/{saved_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    saved_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = db.query(SavedJob).filter(SavedJob.id == saved_id, SavedJob.user_id == current_user.id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(saved)
    db.commit()
    return None

@router.post("/track", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    body: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(db, body.job_id, current_user.id)
    app = JobApplication(
        user_id=current_user.id,
        job_id=body.job_id,
        status=body.status,
        applied_date=body.applied_date,
        notes=body.notes,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return ApplicationResponse(
        id=app.id, job_id=app.job_id, status=app.status,
        applied_date=app.applied_date, notes=app.notes,
        created_at=app.created_at, updated_at=app.updated_at,
        job_title=job.title, job_company=job.company
    )

@router.get("/track", response_model=List[ApplicationResponse])
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    if status_filter:
        q = q.filter(JobApplication.status == status_filter)
    apps = q.order_by(JobApplication.updated_at.desc()).all()
    results = []
    for a in apps:
        job = db.query(JobDescription).get(a.job_id)
        results.append(ApplicationResponse(
            id=a.id, job_id=a.job_id, status=a.status,
            applied_date=a.applied_date, notes=a.notes,
            created_at=a.created_at, updated_at=a.updated_at,
            job_title=job.title if job else None, job_company=job.company if job else None
        ))
    return results

@router.put("/track/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: int,
    body: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = db.query(JobApplication).filter(
        JobApplication.id == app_id, JobApplication.user_id == current_user.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if body.status is not None:
        app.status = body.status
    if body.applied_date is not None:
        app.applied_date = body.applied_date
    if body.notes is not None:
        app.notes = body.notes
    db.commit()
    db.refresh(app)
    job = db.query(JobDescription).get(app.job_id)
    return ApplicationResponse(
        id=app.id, job_id=app.job_id, status=app.status,
        applied_date=app.applied_date, notes=app.notes,
        created_at=app.created_at, updated_at=app.updated_at,
        job_title=job.title if job else None, job_company=job.company if job else None
    )

@router.delete("/track/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app = db.query(JobApplication).filter(
        JobApplication.id == app_id, JobApplication.user_id == current_user.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
    return None
