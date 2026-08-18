from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path) -> str:
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        return ""


def extract_text_from_docx(file_path: Path) -> str:
    try:
        from docx import Document

        doc = Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error("DOCX extraction failed: %s", e)
        return ""


def extract_text_from_txt(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error("TXT extraction failed: %s", e)
        return ""


def extract_resume_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        return extract_text_from_docx(file_path)
    elif suffix == ".txt":
        return extract_text_from_txt(file_path)
    else:
        logger.error("Unsupported file format: %s", suffix)
        return ""


def parse_resume_with_claude(raw_text: str, api_key: str) -> dict:
    """Use Claude to extract structured data from resume text."""
    import anthropic

    if not api_key:
        logger.warning("No Anthropic API key, using basic extraction")
        return _basic_parse(raw_text)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Extract ALL information from this resume into a structured JSON profile.
Only include information explicitly stated in the resume. Never infer or fabricate.
If a field is not found, use empty string, empty list, or null as appropriate.

Return ONLY valid JSON with these fields:
{{
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "summary": "string (professional summary if present)",
  "experience_years": "number or null",
  "current_role": "string (most recent job title)",
  "employers": ["list of employer/company names"],
  "technologies": ["list of ALL technologies, tools, frameworks mentioned"],
  "certifications": ["list of certifications"],
  "education": ["list of education entries"],
  "projects": ["list of notable projects described"],
  "achievements": ["list of quantified achievements/metrics"],
  "aws_experience": ["specific AWS services/tools mentioned"],
  "kubernetes_experience": ["specific K8s tools/services mentioned"],
  "terraform_experience": ["specific IaC tools/services mentioned"],
  "cicd_experience": ["specific CI/CD tools mentioned"],
  "devsecops_experience": ["specific security tools/practices mentioned"],
  "python_experience": ["specific Python tools/libraries mentioned"],
  "gitops_experience": ["specific GitOps tools mentioned"],
  "linux_experience": ["specific Linux/systems skills mentioned"],
  "observability_experience": ["specific monitoring/observability tools mentioned"],
  "docker_experience": ["specific container tools mentioned"]
}}

Resume text:
---
{raw_text[:15000]}
---"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.content[0].text
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        return json.loads(result_text)
    except Exception as e:
        logger.error("Claude resume parsing failed: %s", e)
        return _basic_parse(raw_text)


def _basic_parse(text: str) -> dict:
    """Basic fallback parser when Claude is unavailable."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return {
        "full_name": lines[0] if lines else "",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "experience_years": None,
        "current_role": "",
        "employers": [],
        "technologies": [],
        "certifications": [],
        "education": [],
        "projects": [],
        "achievements": [],
        "aws_experience": [],
        "kubernetes_experience": [],
        "terraform_experience": [],
        "cicd_experience": [],
        "devsecops_experience": [],
        "python_experience": [],
        "gitops_experience": [],
        "linux_experience": [],
        "observability_experience": [],
        "docker_experience": [],
    }
