import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.models.resume import Resume, ParsedProfile
from app.models.user import User
from app.ml.text_extractor import extract_text
from app.ml.resume_parser import parse_resume

def ensure_upload_dir():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

async def save_upload(file: UploadFile, user_id: int) -> tuple:
    ensure_upload_dir()
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB} MB"
        )
    if len(content) < 50:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File appears empty or corrupted")

    unique_name = f"{user_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    return unique_name, file_path, ext, len(content)

def process_resume(db: Session, user: User, filename: str, original_filename: str,
                   file_path: str, file_type: str, file_size: int) -> Resume:
    try:
        raw_text = extract_text(file_path, file_type)
    except Exception as e:
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not raw_text or len(raw_text.strip()) < 30:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Could not extract meaningful text from the document")

    resume = Resume(
        user_id=user.id,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        raw_text=raw_text[:50000],  # limit storage
    )
    db.add(resume)
    db.flush()

    parsed = parse_resume(raw_text)
    profile = ParsedProfile(
        resume_id=resume.id,
        name=parsed.get("name"),
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        summary=parsed.get("summary"),
        skills=parsed.get("skills") or [],
        experience=parsed.get("experience") or [],
        education=parsed.get("education") or [],
        projects=parsed.get("projects") or [],
        certifications=parsed.get("certifications") or [],
        completeness_score=parsed.get("completeness_score", 0.0),
        strengths=parsed.get("strengths") or [],
        weaknesses=parsed.get("weaknesses") or [],
        suggestions=parsed.get("suggestions") or [],
    )
    db.add(profile)
    db.commit()
    db.refresh(resume)
    return resume

def get_user_resumes(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()

def get_resume_or_404(db: Session, resume_id: int, user_id: int) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume

def delete_resume(db: Session, resume: Resume):
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except OSError:
            pass
    db.delete(resume)
    db.commit()
