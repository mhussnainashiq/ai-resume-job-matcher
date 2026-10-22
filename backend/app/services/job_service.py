from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from app.models.job import JobDescription
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate

def create_job(db: Session, user: User, data: JobCreate) -> JobDescription:
    job = JobDescription(
        user_id=user.id,
        title=data.title,
        company=data.company,
        description=data.description,
        required_skills=data.required_skills or [],
        preferred_skills=data.preferred_skills or [],
        experience_required=data.experience_required,
        education_required=data.education_required,
        location=data.location,
        is_sample=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_user_jobs(db: Session, user_id: int, include_samples: bool = True, skip: int = 0, limit: int = 50):
    q = db.query(JobDescription)
    if include_samples:
        q = q.filter((JobDescription.user_id == user_id) | (JobDescription.is_sample == True))
    else:
        q = q.filter(JobDescription.user_id == user_id)
    return q.order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()

def get_job_or_404(db: Session, job_id: int, user_id: Optional[int] = None) -> JobDescription:
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    # Samples are public; user jobs require ownership
    if not job.is_sample and user_id is not None and job.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this job")
    return job

def update_job(db: Session, job: JobDescription, data: JobUpdate) -> JobDescription:
    if job.is_sample:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit sample jobs")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job: JobDescription):
    if job.is_sample:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete sample jobs")
    db.delete(job)
    db.commit()

def seed_sample_jobs(db: Session):
    """Load sample jobs if none exist."""
    existing = db.query(JobDescription).filter(JobDescription.is_sample == True).count()
    if existing > 0:
        return
    samples = [
        {
            "title": "Senior Python Backend Engineer",
            "company": "TechNova Solutions (Sample)",
            "description": "We are looking for a Senior Python Backend Engineer with strong experience in FastAPI, Django, or Flask. You will design and build scalable APIs, work with PostgreSQL and Redis, implement authentication, and collaborate with frontend teams. Experience with Docker, Kubernetes, and AWS is highly valued. You should have solid understanding of software design patterns, testing, and CI/CD pipelines.",
            "required_skills": ["python", "fastapi", "sql", "postgresql", "docker", "git"],
            "preferred_skills": ["kubernetes", "aws", "redis", "ci/cd", "django"],
            "experience_required": "5+ years",
            "education_required": "Bachelor's in CS or related",
            "location": "Remote",
        },
        {
            "title": "Machine Learning Engineer",
            "company": "DataMind AI (Sample)",
            "description": "Join our ML team to build production NLP and recommendation systems. Responsibilities include feature engineering, model training with scikit-learn and PyTorch, deploying models via FastAPI, and monitoring performance. Strong Python, pandas, numpy, and experience with sentence transformers or similar embedding models preferred. Knowledge of MLOps practices is a plus.",
            "required_skills": ["python", "machine learning", "scikit-learn", "pandas", "numpy", "nlp"],
            "preferred_skills": ["pytorch", "tensorflow", "docker", "aws", "fastapi"],
            "experience_required": "3+ years",
            "education_required": "Master's preferred",
            "location": "Hybrid - San Francisco",
        },
        {
            "title": "Full Stack Developer (React + Node)",
            "company": "CloudBridge Inc (Sample)",
            "description": "Build modern web applications using React, Node.js, and Express. You will implement responsive UIs, RESTful APIs, authentication with JWT, and integrate with PostgreSQL. Experience with TypeScript, Redux, and cloud deployment on AWS or Azure is preferred. Strong communication and agile experience required.",
            "required_skills": ["javascript", "react", "node.js", "express", "sql", "git"],
            "preferred_skills": ["typescript", "postgresql", "aws", "docker", "redux"],
            "experience_required": "3+ years",
            "education_required": "Bachelor's degree",
            "location": "New York, NY",
        },
        {
            "title": "Data Analyst",
            "company": "Insight Analytics (Sample)",
            "description": "Analyze business data, create dashboards, and deliver insights. Required skills include SQL, Python, pandas, and data visualization. Experience with statistics, A/B testing, and tools like Tableau or Power BI is preferred. Strong communication skills to present findings to stakeholders.",
            "required_skills": ["sql", "python", "pandas", "data analysis", "statistics"],
            "preferred_skills": ["machine learning", "communication", "excel"],
            "experience_required": "2+ years",
            "education_required": "Bachelor's in quantitative field",
            "location": "Remote",
        },
        {
            "title": "DevOps Engineer",
            "company": "ScaleOps (Sample)",
            "description": "Manage CI/CD pipelines, container orchestration with Kubernetes, and cloud infrastructure on AWS. You will automate deployments, monitor systems, and improve reliability. Experience with Terraform, Docker, Jenkins or GitHub Actions, and Linux is essential.",
            "required_skills": ["docker", "kubernetes", "aws", "linux", "ci/cd", "git"],
            "preferred_skills": ["terraform", "jenkins", "python"],
            "experience_required": "4+ years",
            "education_required": "Bachelor's preferred",
            "location": "Austin, TX",
        },
    ]
    for s in samples:
        job = JobDescription(user_id=None, is_sample=True, **s)
        db.add(job)
    db.commit()
