from __future__ import annotations

import hashlib
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def generate_job_fingerprint(title: str, company: str, url: str) -> str:
    """Create a fingerprint for deduplication based on normalized title+company+url."""
    normalized = f"{title.lower().strip()}|{company.lower().strip()}|{url.lower().strip()}"
    return hashlib.sha256(normalized.encode()).hexdigest()


def normalize_for_dedup(title: str) -> str:
    """Normalize job title for fuzzy deduplication."""
    import re

    title = title.lower().strip()
    # Remove common variations
    title = re.sub(r"\b(senior|sr|jr|junior|lead|principal|staff)\b\.?", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def is_duplicate(job: dict, existing_fingerprints: set[str]) -> bool:
    """Check if job is an exact duplicate based on fingerprint."""
    fp = generate_job_fingerprint(job["title"], job["company"], job["url"])
    return fp in existing_fingerprints


def is_fuzzy_duplicate(
    job: dict, existing_jobs: list[dict], threshold: float = 0.85
) -> bool:
    """Check if job is a fuzzy duplicate of an existing job (same company + similar title)."""
    norm_title = normalize_for_dedup(job["title"])
    company = job["company"].lower().strip()

    for existing in existing_jobs:
        if existing["company"].lower().strip() != company:
            continue
        existing_title = normalize_for_dedup(existing["title"])
        similarity = SequenceMatcher(None, norm_title, existing_title).ratio()
        if similarity >= threshold:
            return True

    return False


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """Remove duplicates from a list of jobs."""
    seen_fingerprints: set[str] = set()
    seen_jobs: list[dict] = []
    unique_jobs = []

    for job in jobs:
        if is_duplicate(job, seen_fingerprints):
            continue
        if is_fuzzy_duplicate(job, seen_jobs):
            continue

        fp = generate_job_fingerprint(job["title"], job["company"], job["url"])
        seen_fingerprints.add(fp)
        seen_jobs.append(job)
        unique_jobs.append(job)

    removed = len(jobs) - len(unique_jobs)
    if removed:
        logger.info("Removed %d duplicate jobs, %d unique remaining", removed, len(unique_jobs))
    return unique_jobs
