from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API keys
    ANTHROPIC_API_KEY: str = ""
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = "apify/linkedin-jobs-scraper"

    # Database
    DATABASE_URL: str = "sqlite:///./jobs.db"

    # Job matching
    JOB_MATCH_THRESHOLD: int = 85
    JOB_SEARCH_HOURS: int = 24

    # Playwright
    PLAYWRIGHT_HEADLESS: bool = True

    # Search targets
    TARGET_COUNTRY: str = "India"

    # Search keywords
    SEARCH_KEYWORDS: list[str] = [
        "DevOps Engineer",
        "Senior DevOps Engineer",
        "DevSecOps Engineer",
        "Senior DevSecOps Engineer",
        "AWS DevOps Engineer",
        "Cloud DevOps Engineer",
        "Platform Engineer",
        "Senior Platform Engineer",
        "Cloud Platform Engineer",
        "SRE",
        "Site Reliability Engineer",
        "DevOps/SRE Engineer",
        "DevSecOps/Platform Engineer",
        "Kubernetes Platform Engineer",
        "Infrastructure Engineer",
    ]

    SEARCH_LOCATIONS: list[str] = [
        "Remote India",
        "India",
        "Hyderabad",
        "Bangalore",
        "Pune",
        "Chennai",
        "Mumbai",
        "Gurgaon",
        "Noida",
        "Delhi NCR",
    ]

    # Scoring weights
    SCORING_WEIGHTS: dict[str, float] = {
        "aws": 15.0,
        "kubernetes": 15.0,
        "terraform": 12.0,
        "cicd": 12.0,
        "devsecops": 12.0,
        "docker": 8.0,
        "gitops": 8.0,
        "python": 6.0,
        "linux": 5.0,
        "observability": 4.0,
        "other": 3.0,
    }

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    GENERATED_DIR: Path = BASE_DIR / "generated"
    RESUMES_DIR: Path = GENERATED_DIR / "resumes"
    COVER_LETTERS_DIR: Path = GENERATED_DIR / "cover_letters"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
