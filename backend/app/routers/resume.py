from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import CandidateProfile
from app.services.resume_parser import extract_resume_text, parse_resume_with_claude

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/resume", tags=["resume"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save uploaded file
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = settings.UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    # Extract text
    raw_text = extract_resume_text(file_path)
    if not raw_text:
        raise HTTPException(status_code=400, detail="Failed to extract text from resume")

    # Parse with Claude
    profile_data = parse_resume_with_claude(raw_text, settings.ANTHROPIC_API_KEY)

    # Upsert candidate profile
    existing = db.query(CandidateProfile).first()
    if existing:
        profile = existing
    else:
        profile = CandidateProfile()
        db.add(profile)

    profile.raw_text = raw_text
    profile.full_name = profile_data.get("full_name", "")
    profile.email = profile_data.get("email", "")
    profile.phone = profile_data.get("phone", "")
    profile.location = profile_data.get("location", "")
    profile.summary = profile_data.get("summary", "")
    profile.experience_years = profile_data.get("experience_years")
    profile.current_role = profile_data.get("current_role", "")
    profile.employers = json.dumps(profile_data.get("employers", []))
    profile.technologies = json.dumps(profile_data.get("technologies", []))
    profile.certifications = json.dumps(profile_data.get("certifications", []))
    profile.education = json.dumps(profile_data.get("education", []))
    profile.projects = json.dumps(profile_data.get("projects", []))
    profile.achievements = json.dumps(profile_data.get("achievements", []))
    profile.aws_experience = json.dumps(profile_data.get("aws_experience", []))
    profile.kubernetes_experience = json.dumps(profile_data.get("kubernetes_experience", []))
    profile.terraform_experience = json.dumps(profile_data.get("terraform_experience", []))
    profile.cicd_experience = json.dumps(profile_data.get("cicd_experience", []))
    profile.devsecops_experience = json.dumps(profile_data.get("devsecops_experience", []))
    profile.python_experience = json.dumps(profile_data.get("python_experience", []))
    profile.gitops_experience = json.dumps(profile_data.get("gitops_experience", []))
    profile.linux_experience = json.dumps(profile_data.get("linux_experience", []))
    profile.observability_experience = json.dumps(profile_data.get("observability_experience", []))
    profile.docker_experience = json.dumps(profile_data.get("docker_experience", []))
    profile.structured_profile = json.dumps(profile_data)

    db.commit()
    db.refresh(profile)

    return {
        "message": "Resume processed successfully",
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "technologies_count": len(json.loads(profile.technologies) if profile.technologies else []),
    }


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(CandidateProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")
    return profile
