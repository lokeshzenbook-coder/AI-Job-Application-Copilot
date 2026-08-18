from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import CandidateProfile, Job, JobStatus
from app.schemas import MatchResult
from app.services.claude_service import match_job_to_resume

logger = logging.getLogger(__name__)
settings = get_settings()


def filter_recent_jobs(jobs: list[dict], hours: int = 24) -> list[dict]:
    """Filter jobs posted within the specified number of hours."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    filtered = []
    for job in jobs:
        posted = job.get("posted_at")
        if posted is None:
            # Include jobs with unknown posting time
            filtered.append(job)
        elif posted >= cutoff:
            filtered.append(job)
        else:
            logger.debug(
                "Filtering out old job: %s at %s (posted %s)",
                job.get("title"),
                job.get("company"),
                posted,
            )
    return filtered


def analyze_jobs(
    db: Session, profile: CandidateProfile, limit: int | None = None
) -> list[MatchResult]:
    """Analyze all DISCOVERED jobs against the candidate profile."""
    query = db.query(Job).filter(Job.status == JobStatus.DISCOVERED.value)
    if limit:
        query = query.limit(limit)

    jobs = query.all()
    resume_profile = json.loads(profile.structured_profile) if profile.structured_profile else {}
    if not resume_profile:
        resume_profile = {
            "full_name": profile.full_name,
            "technologies": json.loads(profile.technologies) if profile.technologies else [],
            "aws_experience": json.loads(profile.aws_experience) if profile.aws_experience else [],
            "kubernetes_experience": json.loads(profile.kubernetes_experience) if profile.kubernetes_experience else [],
            "terraform_experience": json.loads(profile.terraform_experience) if profile.terraform_experience else [],
            "cicd_experience": json.loads(profile.cicd_experience) if profile.cicd_experience else [],
            "devsecops_experience": json.loads(profile.devsecops_experience) if profile.devsecops_experience else [],
            "python_experience": json.loads(profile.python_experience) if profile.python_experience else [],
            "gitops_experience": json.loads(profile.gitops_experience) if profile.gitops_experience else [],
            "linux_experience": json.loads(profile.linux_experience) if profile.linux_experience else [],
            "observability_experience": json.loads(profile.observability_experience) if profile.observability_experience else [],
            "docker_experience": json.loads(profile.docker_experience) if profile.docker_experience else [],
            "experience_years": profile.experience_years,
            "certifications": json.loads(profile.certifications) if profile.certifications else [],
        }

    results = []
    for job in jobs:
        job.status = JobStatus.ANALYZING.value
        db.commit()

        match_result = match_job_to_resume(
            job_description=job.description,
            resume_profile=resume_profile,
            job_title=job.title,
            company=job.company,
        )

        # Update job with match results
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

        # Apply eligibility rules
        if (
            match_result.match_score >= settings.JOB_MATCH_THRESHOLD
            and not match_result.mandatory_gaps
        ):
            job.status = JobStatus.QUEUED.value
        else:
            job.status = JobStatus.MATCHED.value

        db.commit()
        results.append(match_result)
        logger.info(
            "Analyzed %s at %s: score=%.0f, status=%s",
            job.title,
            job.company,
            match_result.match_score,
            job.status,
        )

    return results


def get_eligible_jobs(db: Session) -> list[Job]:
    """Get jobs that meet application eligibility criteria."""
    return (
        db.query(Job)
        .filter(Job.status.in_([JobStatus.QUEUED.value, JobStatus.MATCHED.value]))
        .filter(Job.match_score >= settings.JOB_MATCH_THRESHOLD)
        .all()
    )
