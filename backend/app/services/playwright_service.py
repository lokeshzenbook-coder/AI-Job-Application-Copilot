from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CAPTCHA_SELECTORS = [
    "[class*='captcha']",
    "[id*='captcha']",
    "[class*='recaptcha']",
    "iframe[src*='recaptcha']",
    "[class*='hcaptcha']",
    "iframe[src*='hcaptcha']",
    "[class*='challenge']",
    "#challenge-running",
    "[data-testid='captcha']",
]

MFA_SELECTORS = [
    "[class*='mfa']",
    "[class*='2fa']",
    "[class*='two-factor']",
    "input[name*='code']",
    "input[name*='otp']",
    "input[placeholder*='code']",
    "input[placeholder*='OTP']",
]

LOGIN_SELECTORS = [
    "input[type='password']",
    "input[name='session_key']",
    "input[name='session_password']",
    "[class*='login-form']",
    "form[action*='login']",
]


@dataclass
class FormFillResult:
    success: bool
    status: str  # READY, HUMAN_ACTION_REQUIRED, ERROR
    message: str = ""
    fields_found: list[str] = field(default_factory=list)
    fields_filled: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    page_title: str = ""
    page_url: str = ""


async def open_and_analyze_application_page(
    url: str,
    candidate_data: dict,
    resume_path: str | None = None,
) -> FormFillResult:
    """Open a job application URL, detect form fields, check for blockers."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return FormFillResult(
            success=False,
            status="ERROR",
            message="playwright not installed. Run: pip install playwright && playwright install chromium",
        )

    result = FormFillResult(success=False, status="ERROR")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                result.message = f"Failed to load page: {e}"
                await browser.close()
                return result

            result.page_title = await page.title()
            result.page_url = page.url

            # Check for blockers
            blockers = await _detect_blockers(page)
            if blockers:
                result.status = "HUMAN_ACTION_REQUIRED"
                result.blockers = blockers
                result.message = f"Blocked by: {', '.join(blockers)}"
                await browser.close()
                return result

            # Detect form fields
            fields = await _detect_form_fields(page)
            result.fields_found = [f["name"] or f["type"] for f in fields]

            # Try to fill standard fields
            filled = await _fill_standard_fields(page, candidate_data)
            result.fields_filled = filled

            # Upload resume if path provided
            if resume_path:
                uploaded = await _upload_resume(page, resume_path)
                if uploaded:
                    result.fields_filled.append("resume_upload")

            result.success = True
            result.status = "READY"
            result.message = f"Found {len(fields)} fields, filled {len(filled)}"

            await browser.close()

    except Exception as e:
        logger.error("Playwright workflow failed: %s", e)
        result.message = f"Workflow error: {e}"

    return result


async def _detect_blockers(page) -> list[str]:
    """Detect CAPTCHA, MFA, login walls."""
    blockers = []

    for selector in CAPTCHA_SELECTORS:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                blockers.append("CAPTCHA")
                break
        except Exception:
            continue

    for selector in MFA_SELECTORS:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                blockers.append("MFA/2FA")
                break
        except Exception:
            continue

    for selector in LOGIN_SELECTORS:
        try:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                blockers.append("LOGIN_REQUIRED")
                break
        except Exception:
            continue

    return blockers


async def _detect_form_fields(page) -> list[dict]:
    """Detect all form input fields on the page."""
    fields = []
    inputs = await page.query_selector_all("input, textarea, select")
    for inp in inputs:
        try:
            field_type = await inp.get_attribute("type") or "text"
            name = await inp.get_attribute("name") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            label_text = await _get_associated_label(page, inp)
            visible = await inp.is_visible()
            if visible and field_type not in ("hidden", "submit", "button", "image"):
                fields.append({
                    "type": field_type,
                    "name": name,
                    "placeholder": placeholder,
                    "label": label_text,
                })
        except Exception:
            continue
    return fields


async def _get_associated_label(page, element) -> str:
    """Try to find the label text for a form element."""
    try:
        element_id = await element.get_attribute("id")
        if element_id:
            label = await page.query_selector(f"label[for='{element_id}']")
            if label:
                return (await label.inner_text()).strip()
    except Exception:
        pass
    return ""


async def _fill_standard_fields(page, candidate_data: dict) -> list[str]:
    """Fill standard application form fields with verified candidate data."""
    filled = []

    field_mapping = {
        "first_name": candidate_data.get("first_name", ""),
        "firstname": candidate_data.get("first_name", ""),
        "last_name": candidate_data.get("last_name", ""),
        "lastname": candidate_data.get("last_name", ""),
        "email": candidate_data.get("email", ""),
        "phone": candidate_data.get("phone", ""),
        "telephone": candidate_data.get("phone", ""),
        "mobile": candidate_data.get("phone", ""),
        "location": candidate_data.get("location", ""),
        "city": candidate_data.get("city", ""),
        "linkedin": candidate_data.get("linkedin_url", ""),
        "github": candidate_data.get("github_url", ""),
        "portfolio": candidate_data.get("portfolio_url", ""),
        "website": candidate_data.get("portfolio_url", ""),
        "url": candidate_data.get("portfolio_url", ""),
    }

    for field_name, value in field_mapping.items():
        if not value:
            continue
        selectors = [
            f"input[name*='{field_name}' i]",
            f"input[id*='{field_name}' i]",
            f"input[placeholder*='{field_name}' i]",
        ]
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.fill(value)
                    filled.append(field_name)
                    break
            except Exception:
                continue

    return filled


async def _upload_resume(page, resume_path: str) -> bool:
    """Upload resume to file input if available."""
    try:
        file_input = await page.query_selector("input[type='file']")
        if file_input:
            await file_input.set_input_files(resume_path)
            return True
    except Exception as e:
        logger.error("Resume upload failed: %s", e)
    return False
