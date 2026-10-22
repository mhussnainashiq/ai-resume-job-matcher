from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.services.job_service import create_job, get_user_jobs, get_job_or_404, update_job, delete_job

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_endpoint(
    data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = create_job(db, current_user, data)
    return JobResponse.model_validate(job)

@router.get("", response_model=JobListResponse)
def list_jobs(
    include_samples: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    jobs = get_user_jobs(db, current_user.id, include_samples, skip, limit)
    from app.models.job import JobDescription
    total = db.query(JobDescription).filter(
        (JobDescription.user_id == current_user.id) | (JobDescription.is_sample == True)
    ).count()
    return JobListResponse(jobs=[JobResponse.model_validate(j) for j in jobs], total=total)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(db, job_id, current_user.id)
    return JobResponse.model_validate(job)

@router.put("/{job_id}", response_model=JobResponse)
def update_job_endpoint(
    job_id: int,
    data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(db, job_id, current_user.id)
    if job.is_sample or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot edit this job")
    job = update_job(db, job, data)
    return JobResponse.model_validate(job)

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_endpoint(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_or_404(db, job_id, current_user.id)
    if job.is_sample or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete this job")
    delete_job(db, job)
    return None
