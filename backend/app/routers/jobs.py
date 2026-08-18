from __future__ import annotations

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Application, CandidateProfile, Job, JobStatus
from app.schemas import MatchResult
from app.services.apify_service import search_linkedin_jobs
from app.services.dedup import deduplicate_jobs
from app.services.job_matcher import analyze_jobs, filter_recent_jobs

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search")
def search_jobs(db: Session = Depends(get_db)):
    """Search LinkedIn jobs via Apify, filter, deduplicate."""
    # Fetch from Apify
    raw_jobs = search_linkedin_jobs()
    if not raw_jobs:
        return {"message": "No jobs found from Apify", "count": 0}

    # Filter to 24h
    recent_jobs = filter_recent_jobs(raw_jobs, hours=settings.JOB_SEARCH_HOURS)

    # Deduplicate
    unique_jobs = deduplicate_jobs(recent_jobs)

    # Store in DB
    added = 0
    for job_data in unique_jobs:
        existing = db.query(Job).filter(Job.url == job_data["url"]).first()
        if existing:
            continue
        job = Job(
            company=job_data["company"],
            title=job_data["title"],
            location=job_data.get("location", ""),
            remote_type=job_data.get("remote_type", ""),
            posted_at=job_data.get("posted_at"),
            url=job_data["url"],
            description=job_data.get("description", ""),
            status=JobStatus.DISCOVERED.value,
        )
        db.add(job)
        added += 1

    db.commit()

    return {
        "message": f"Found {len(raw_jobs)} raw jobs, {len(recent_jobs)} within 24h, {len(unique_jobs)} unique, {added} new",
        "raw_count": len(raw_jobs),
        "recent_count": len(recent_jobs),
        "unique_count": len(unique_jobs),
        "new_count": added,
    }


@router.get("")
def list_jobs(
    status: str | None = None,
    min_score: float | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if min_score is not None:
        query = query.filter(Job.match_score >= min_score)
    query = query.order_by(Job.match_score.desc().nullslast(), Job.created_at.desc())
    total = query.count()
    jobs = query.offset(offset).limit(limit).all()
    return {"total": total, "jobs": jobs}


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/analyze")
def analyze_all_jobs(db: Session = Depends(get_db)):
    """Analyze all discovered jobs against the candidate profile."""
    profile = db.query(CandidateProfile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No resume uploaded. Upload resume first.")

    results = analyze_jobs(db, profile, limit=None)

    return {
        "message": f"Analyzed {len(results)} jobs",
        "analyzed_count": len(results),
    }


@router.post("/{job_id}/analyze-single")
def analyze_single_job(job_id: int, db: Session = Depends(get_db)):
    """Analyze a single specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(CandidateProfile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No resume uploaded")

    resume_profile = json.loads(profile.structured_profile) if profile.structured_profile else {}

    job.status = JobStatus.ANALYZING.value
    db.commit()

    from app.services.claude_service import match_job_to_resume
    match_result = match_job_to_resume(
        job_description=job.description,
        resume_profile=resume_profile,
        job_title=job.title,
        company=job.company,
    )

    job.match_score = match_result.match_score
    job.interview_probability = match_result.interview_probability
    job.recommendation = match_result.recommendation
    job.experience_match = match_result.experience_match
    job.aws_match = match_result.aws_match
    job.kubernetes_match = match_result.kubernetes_match
    job.terraform_match = match_result.terraform_match
    job.cicd_match = match_result.cicd_match
    job.devsecops_match = match_result.devsecops_match
    job.python_match = match_result.python_match
    job.gitops_match = match_result.gitops_match
    job.mandatory_gaps = json.dumps(match_result.mandatory_gaps)
    job.nice_to_have_gaps = json.dumps(match_result.nice_to_have_gaps)
    job.match_reason = match_result.reason

    if (
        match_result.match_score >= settings.JOB_MATCH_THRESHOLD
        and not match_result.mandatory_gaps
    ):
        job.status = JobStatus.QUEUED.value
        # Create application entry
        app_entry = Application(job_id=job.id, status=JobStatus.QUEUED.value)
        db.add(app_entry)
    else:
        job.status = JobStatus.MATCHED.value

    db.commit()
    return match_result


@router.post("/{job_id}/tailor-resume")
def tailor_resume(job_id: int, db: Session = Depends(get_db)):
    """Generate a tailored resume for the job."""
    from pathlib import Path

    from app.services.claude_service import tailor_resume as tailor

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(CandidateProfile).first()
    if not profile or not profile.raw_text:
        raise HTTPException(status_code=400, detail="No resume text available")

    tailored = tailor(
        resume_text=profile.raw_text,
        job_description=job.description,
        job_title=job.title,
        company=job.company,
    )

    # Save to generated directory
    settings.RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{job.company}_{job.title}".replace(" ", "_").replace("/", "_")[:100]
    file_path = settings.RESUMES_DIR / f"{safe_name}_tailored.txt"
    file_path.write_text(tailored, encoding="utf-8")

    # Update application if exists
    app_entry = db.query(Application).filter(Application.job_id == job_id).first()
    if app_entry:
        app_entry.resume_version = str(file_path)
        db.commit()

    return {"message": "Resume tailored", "file_path": str(file_path), "preview": tailored[:500]}


@router.post("/{job_id}/cover-letter")
def generate_cover_letter(job_id: int, db: Session = Depends(get_db)):
    """Generate a cover letter for the job."""
    from pathlib import Path

    from app.services.claude_service import generate_cover_letter as gen_letter

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = db.query(CandidateProfile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No resume uploaded")

    resume_profile = json.loads(profile.structured_profile) if profile.structured_profile else {}

    letter = gen_letter(
        resume_profile=resume_profile,
        job_description=job.description,
        job_title=job.title,
        company=job.company,
    )

    # Save
    settings.COVER_LETTERS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{job.company}_{job.title}".replace(" ", "_").replace("/", "_")[:100]
    file_path = settings.COVER_LETTERS_DIR / f"{safe_name}_cover.txt"
    file_path.write_text(letter, encoding="utf-8")

    # Update application
    app_entry = db.query(Application).filter(Application.job_id == job_id).first()
    if not app_entry:
        app_entry = Application(job_id=job.id, status=JobStatus.QUEUED.value)
        db.add(app_entry)
    app_entry.cover_letter = letter
    db.commit()

    return {"message": "Cover letter generated", "file_path": str(file_path), "preview": letter[:500]}
