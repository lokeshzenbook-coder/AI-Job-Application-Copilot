from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    DISCOVERED = "DISCOVERED"
    ANALYZING = "ANALYZING"
    MATCHED = "MATCHED"
    QUEUED = "QUEUED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"


class InterviewProbability(str, enum.Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(500), nullable=False)
    title = Column(String(500), nullable=False)
    location = Column(String(500), default="")
    remote_type = Column(String(100), default="")
    posted_at = Column(DateTime, nullable=True)
    url = Column(Text, nullable=False)
    description = Column(Text, default="")
    match_score = Column(Float, nullable=True)
    interview_probability = Column(String(50), nullable=True)
    recommendation = Column(String(50), nullable=True)
    experience_match = Column(Float, nullable=True)
    aws_match = Column(Float, nullable=True)
    kubernetes_match = Column(Float, nullable=True)
    terraform_match = Column(Float, nullable=True)
    cicd_match = Column(Float, nullable=True)
    devsecops_match = Column(Float, nullable=True)
    python_match = Column(Float, nullable=True)
    gitops_match = Column(Float, nullable=True)
    mandatory_gaps = Column(Text, default="[]")
    nice_to_have_gaps = Column(Text, default="[]")
    match_reason = Column(Text, default="")
    status = Column(
        String(50), default=JobStatus.DISCOVERED.value
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    application = relationship("Application", back_populates="job", uselist=False)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_version = Column(String(500), default="")
    cover_letter = Column(Text, default="")
    application_url = Column(Text, default="")
    status = Column(
        String(50), default=JobStatus.DISCOVERED.value
    )
    applied_at = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="application")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text, default="")
    full_name = Column(String(500), default="")
    email = Column(String(500), default="")
    phone = Column(String(100), default="")
    location = Column(String(500), default="")
    summary = Column(Text, default="")
    experience_years = Column(Float, nullable=True)
    current_role = Column(String(500), default="")
    employers = Column(Text, default="[]")
    technologies = Column(Text, default="[]")
    certifications = Column(Text, default="[]")
    education = Column(Text, default="[]")
    projects = Column(Text, default="[]")
    achievements = Column(Text, default="[]")
    aws_experience = Column(Text, default="[]")
    kubernetes_experience = Column(Text, default="[]")
    terraform_experience = Column(Text, default="[]")
    cicd_experience = Column(Text, default="[]")
    devsecops_experience = Column(Text, default="[]")
    python_experience = Column(Text, default="[]")
    gitops_experience = Column(Text, default="[]")
    linux_experience = Column(Text, default="[]")
    observability_experience = Column(Text, default="[]")
    docker_experience = Column(Text, default="[]")
    structured_profile = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
