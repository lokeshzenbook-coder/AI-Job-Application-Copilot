from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Application, CandidateProfile, Job, JobStatus
from app.services.playwright_service import open_and_analyze_application_page

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("")
def list_applications(
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    from sqlalchemy.orm import joinedload

    query = db.query(Application).options(joinedload(Application.job))
    if status:
        query = query.filter(Application.status == status)
    query = query.order_by(Application.created_at.desc())
    total = query.count()
    apps = query.offset(offset).limit(limit).all()
    return {"total": total, "applications": apps}


@router.post("/{app_id}/prepare")
def prepare_application(app_id: int, db: Session = Depends(get_db)):
    """Prepare application: mark ready for human review."""
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    job = app_entry.job
    if not job:
        raise HTTPException(status_code=400, detail="Associated job not found")

    app_entry.status = JobStatus.READY_FOR_REVIEW.value
    db.commit()

    return {
        "message": "Application prepared for review",
        "application_id": app_entry.id,
        "company": job.company,
        "title": job.title,
        "match_score": job.match_score,
        "resume_version": app_entry.resume_version,
        "cover_letter_preview": app_entry.cover_letter[:300] if app_entry.cover_letter else "",
        "status": app_entry.status,
    }


@router.post("/{app_id}/approve")
def approve_application(app_id: int, db: Session = Depends(get_db)):
    """Approve application for submission (human approval gate)."""
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_entry.status not in (JobStatus.READY_FOR_REVIEW.value, JobStatus.QUEUED.value):
        raise HTTPException(
            status_code=400,
            detail=f"Application in status '{app_entry.status}' cannot be approved. Must be READY_FOR_REVIEW or QUEUED.",
        )

    app_entry.status = JobStatus.SUBMITTED.value
    app_entry.notes = "Approved by user"
    db.commit()

    return {"message": "Application approved", "status": app_entry.status}


@router.post("/{app_id}/cancel")
def cancel_application(app_id: int, reason: str = "", db: Session = Depends(get_db)):
    """Cancel an application."""
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    app_entry.status = JobStatus.WITHDRAWN.value
    app_entry.notes = f"Cancelled: {reason}" if reason else "Cancelled by user"
    db.commit()

    return {"message": "Application cancelled", "status": app_entry.status}


@router.post("/{app_id}/fill-form")
async def fill_application_form(app_id: int, db: Session = Depends(get_db)):
    """Use Playwright to open and fill an application form. Never submits."""
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    job = app_entry.job
    if not job:
        raise HTTPException(status_code=400, detail="Associated job not found")

    if not job.url:
        raise HTTPException(status_code=400, detail="No application URL available")

    profile = db.query(CandidateProfile).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No resume uploaded")

    # Build candidate data from profile
    candidate_data = {
        "first_name": profile.full_name.split()[0] if profile.full_name else "",
        "last_name": " ".join(profile.full_name.split()[1:]) if profile.full_name and len(profile.full_name.split()) > 1 else "",
        "email": profile.email,
        "phone": profile.phone,
        "location": profile.location,
    }

    # Find resume path if tailored version exists
    resume_path = None
    if app_entry.resume_version and Path(app_entry.resume_version).exists():
        resume_path = app_entry.resume_version

    result = await open_and_analyze_application_page(
        url=job.url,
        candidate_data=candidate_data,
        resume_path=resume_path,
    )

    if result.status == "HUMAN_ACTION_REQUIRED":
        app_entry.status = JobStatus.READY_FOR_REVIEW.value
        app_entry.notes = f"Blocked: {', '.join(result.blockers)}"
    elif result.status == "READY":
        app_entry.notes = f"Form analyzed: {result.message}"

    db.commit()

    return {
        "status": result.status,
        "message": result.message,
        "page_title": result.page_title,
        "page_url": result.page_url,
        "fields_found": result.fields_found,
        "fields_filled": result.fields_filled,
        "blockers": result.blockers,
    }


@router.post("/{app_id}/submit")
async def submit_application(app_id: int, db: Session = Depends(get_db)):
    """Submit application via Playwright. Only after explicit human approval."""
    app_entry = db.query(Application).filter(Application.id == app_id).first()
    if not app_entry:
        raise HTTPException(status_code=404, detail="Application not found")

    if app_entry.status != JobStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Application must be SUBMITTED status (current: {app_entry.status}). Approve first.",
        )

    # This endpoint is the final gate - in production, this would
    # trigger Playwright to actually submit the form.
    # For safety, we log and mark as submitted but do NOT auto-submit.
    logger.info(
        "Application %d approved for submission to %s. Manual submission required.",
        app_id,
        app_entry.job.url if app_entry.job else "unknown",
    )

    return {
        "message": "Application ready for submission. Please submit manually.",
        "status": app_entry.status,
        "job_url": app_entry.job.url if app_entry.job else "",
    }
