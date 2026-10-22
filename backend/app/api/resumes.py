from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListResponse, ResumeUploadResponse
from app.services.resume_service import save_upload, process_resume, get_user_resumes, get_resume_or_404, delete_resume

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    filename, file_path, ext, size = await save_upload(file, current_user.id)
    resume = process_resume(db, current_user, filename, file.filename or "resume", file_path, ext, size)
    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        original_filename=resume.original_filename,
        file_type=resume.file_type,
        file_size=resume.file_size,
        created_at=resume.created_at,
    )

@router.get("", response_model=ResumeListResponse)
def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = get_user_resumes(db, current_user.id, skip, limit)
    total = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    return ResumeListResponse(
        resumes=[ResumeResponse.model_validate(r) for r in resumes],
        total=total,
    )

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = get_resume_or_404(db, resume_id, current_user.id)
    return ResumeResponse.model_validate(resume)

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = get_resume_or_404(db, resume_id, current_user.id)
    delete_resume(db, resume)
    return None
