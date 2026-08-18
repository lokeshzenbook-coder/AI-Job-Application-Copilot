from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class JobBase(BaseModel):
    company: str
    title: str
    location: str = ""
    remote_type: str = ""
    posted_at: datetime | None = None
    url: str
    description: str = ""


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    match_score: float | None = None
    interview_probability: str | None = None
    recommendation: str | None = None
    experience_match: float | None = None
    aws_match: float | None = None
    kubernetes_match: float | None = None
    terraform_match: float | None = None
    cicd_match: float | None = None
    devsecops_match: float | None = None
    python_match: float | None = None
    gitops_match: float | None = None
    mandatory_gaps: str = "[]"
    nice_to_have_gaps: str = "[]"
    match_reason: str = ""
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchResult(BaseModel):
    match_score: float
    interview_probability: str
    recommendation: str
    experience_match: float = 0.0
    aws_match: float = 0.0
    kubernetes_match: float = 0.0
    terraform_match: float = 0.0
    cicd_match: float = 0.0
    devsecops_match: float = 0.0
    python_match: float = 0.0
    gitops_match: float = 0.0
    mandatory_gaps: list[str] = []
    nice_to_have_gaps: list[str] = []
    reason: str = ""


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    resume_version: str = ""
    cover_letter: str = ""
    application_url: str = ""
    status: str
    applied_at: datetime | None = None
    interview_date: datetime | None = None
    notes: str = ""
    created_at: datetime
    updated_at: datetime
    job: JobResponse | None = None

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_jobs: int = 0
    jobs_last_24h: int = 0
    unique_jobs: int = 0
    strong_matches: int = 0
    applications_ready: int = 0
    submitted: int = 0
    interviews: int = 0
    rejected: int = 0


class CandidateProfileResponse(BaseModel):
    id: int
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    experience_years: float | None = None
    current_role: str = ""
    employers: str = "[]"
    technologies: str = "[]"
    certifications: str = "[]"
    education: str = "[]"
    projects: str = "[]"
    achievements: str = "[]"
    structured_profile: str = "{}"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeTailorRequest(BaseModel):
    job_id: int


class CoverLetterRequest(BaseModel):
    job_id: int
