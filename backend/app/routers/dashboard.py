from __future__ import annotations

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Job, JobStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)

    total_jobs = db.query(Job).count()
    jobs_last_24h = db.query(Job).filter(Job.created_at >= cutoff_24h).count()

    # Count unique URLs
    unique_urls = db.query(Job.url).distinct().count()

    strong_matches = db.query(Job).filter(
        Job.match_score >= 85,
        Job.match_score.isnot(None),
    ).count()

    applications_ready = db.query(Application).filter(
        Application.status.in_([
            JobStatus.QUEUED.value,
            JobStatus.READY_FOR_REVIEW.value,
        ])
    ).count()

    submitted = db.query(Application).filter(
        Application.status == JobStatus.SUBMITTED.value
    ).count()

    interviews = db.query(Application).filter(
        Application.status == JobStatus.INTERVIEW.value
    ).count()

    rejected = db.query(Job).filter(
        Job.status == JobStatus.REJECTED.value
    ).count()

    return {
        "total_jobs": total_jobs,
        "jobs_last_24h": jobs_last_24h,
        "unique_jobs": unique_urls,
        "strong_matches": strong_matches,
        "applications_ready": applications_ready,
        "submitted": submitted,
        "interviews": interviews,
        "rejected": rejected,
    }
