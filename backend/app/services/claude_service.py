from __future__ import annotations

import json
import logging

import anthropic

from app.config import get_settings
from app.schemas import MatchResult

logger = logging.getLogger(__name__)
settings = get_settings()


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def match_job_to_resume(
    job_description: str, resume_profile: dict, job_title: str = "", company: str = ""
) -> MatchResult:
    """Use Claude to analyze JD vs resume and produce structured scoring."""
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("No Anthropic API key, returning low-confidence match")
        return MatchResult(
            match_score=0,
            interview_probability="LOW",
            recommendation="MANUAL_REVIEW",
            reason="Claude API key not configured",
        )

    client = get_client()

    weights_desc = "\n".join(
        f"  {k}: {v}%" for k, v in settings.SCORING_WEIGHTS.items()
    )

    prompt = f"""You are an expert technical recruiter analyzing a job description against a candidate's resume.

TASK: Compare the COMPLETE job description against the candidate's resume profile.
Be CONSERVATIVE. A keyword mention alone does NOT mean experience. The candidate must demonstrate substantial experience in a technology area to score well.

Scoring weights (use these to calculate the overall match_score):
{weights_desc}

For each category, score 0-100 based on how well the resume demonstrates relevant experience.

IMPORTANT RULES:
- Do NOT inflate scores. If resume shows basic mention, score proportionally low.
- If mandatory requirements are not met, set recommendation to REJECT regardless of score.
- Interview probability should reflect real likelihood based on evidence in resume.
- mandatory_gaps: list skills that are REQUIRED by the JD but MISSING from resume entirely.
- nice_to_have_gaps: list skills that are preferred but not mandatory and missing.

Return ONLY valid JSON matching this exact schema:
{{
  "match_score": "number 0-100 (weighted average)",
  "interview_probability": "VERY_HIGH|HIGH|MEDIUM|LOW",
  "recommendation": "APPLY|MANUAL_REVIEW|REJECT",
  "experience_match": "number 0-100",
  "aws_match": "number 0-100",
  "kubernetes_match": "number 0-100",
  "terraform_match": "number 0-100",
  "cicd_match": "number 0-100",
  "devsecops_match": "number 0-100",
  "python_match": "number 0-100",
  "gitops_match": "number 0-100",
  "mandatory_gaps": ["list of missing mandatory skills"],
  "nice_to_have_gaps": ["list of missing nice-to-have skills"],
  "reason": "concise explanation of the match assessment"
}}

Job Title: {job_title}
Company: {company}

Job Description:
---
{job_description[:8000]}
---

Candidate Resume Profile:
---
{json.dumps(resume_profile, indent=2)[:10000]}
---"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.content[0].text
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        data = json.loads(result_text)
        return MatchResult(**data)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Claude matching response as JSON: %s", e)
        return MatchResult(
            match_score=0,
            interview_probability="LOW",
            recommendation="MANUAL_REVIEW",
            reason=f"AI response parsing failed: {e}",
        )
    except Exception as e:
        logger.error("Claude matching failed: %s", e)
        return MatchResult(
            match_score=0,
            interview_probability="LOW",
            recommendation="MANUAL_REVIEW",
            reason=f"AI matching error: {e}",
        )


def tailor_resume(
    resume_text: str, job_description: str, job_title: str, company: str
) -> str:
    """Generate a tailored resume emphasizing relevant experience."""
    if not settings.ANTHROPIC_API_KEY:
        return resume_text

    client = get_client()

    prompt = f"""You are a professional resume writer. Tailor this resume for the specific job below.

RULES:
1. ONLY use information present in the original resume. NEVER invent experience, skills, certifications, employers, dates, or metrics.
2. Reorder and rephrase sections to emphasize relevance to this job.
3. Optimize for ATS keywords that are supported by the resume.
4. Maintain all factual information accurately.
5. Keep the resume concise and professional.

Job Title: {job_title}
Company: {company}

Job Description:
---
{job_description[:5000]}
---

Original Resume:
---
{resume_text[:10000]}
---

Return the tailored resume as formatted text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Resume tailoring failed: %s", e)
        return resume_text


def generate_cover_letter(
    resume_profile: dict, job_description: str, job_title: str, company: str
) -> str:
    """Generate a concise, job-specific cover letter."""
    if not settings.ANTHROPIC_API_KEY:
        return ""

    client = get_client()

    prompt = f"""Write a concise, professional cover letter for this job application.

RULES:
1. Maximum 3 paragraphs.
2. Reference ONLY experience and skills from the resume profile.
3. Mention 2-3 specific relevant strengths.
4. Do NOT use generic AI filler language.
5. Do NOT invent any experience.
6. Address the hiring manager.

Job Title: {job_title}
Company: {company}

Job Description:
---
{job_description[:5000]}
---

Candidate Profile:
---
{json.dumps(resume_profile, indent=2)[:8000]}
---"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Cover letter generation failed: %s", e)
        return ""
