from __future__ import annotations

import logging
from datetime import datetime, timedelta

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def search_linkedin_jobs(
    keywords: list[str] | None = None,
    locations: list[str] | None = None,
    max_items_per_search: int = 25,
) -> list[dict]:
    """Search LinkedIn jobs via Apify and return raw job data."""
    if not settings.APIFY_API_TOKEN:
        logger.warning("No Apify API token configured")
        return []

    try:
        from apify_client import ApifyClient
    except ImportError:
        logger.error("apify-client not installed. Run: pip install apify-client")
        return []

    client = ApifyClient(settings.APIFY_ACTOR_ID)
    all_jobs = []
    search_keywords = keywords or settings.SEARCH_KEYWORDS
    search_locations = locations or settings.SEARCH_LOCATIONS

    for keyword in search_keywords:
        for location in search_locations:
            try:
                run_input = {
                    "searchUrl": f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}",
                    "maxItems": max_items_per_search,
                }
                run = client.call(run_input)
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    job = _normalize_job(item, keyword, location)
                    if job:
                        all_jobs.append(job)
            except Exception as e:
                logger.error(
                    "Apify search failed for '%s' in '%s': %s", keyword, location, e
                )
                continue

    logger.info("Total raw jobs fetched: %d", len(all_jobs))
    return all_jobs


def _normalize_job(raw: dict, search_keyword: str, search_location: str) -> dict | None:
    """Normalize Apify LinkedIn job data into our schema."""
    try:
        title = raw.get("title", "").strip()
        company = raw.get("companyName", "").strip()
        url = raw.get("url", "") or raw.get("jobUrl", "")

        if not title or not company or not url:
            return None

        # Parse posted date
        posted_at = None
        date_text = raw.get("postedAt", "") or raw.get("listedAt", "")
        if date_text:
            posted_at = _parse_relative_date(date_text)

        description = raw.get("description", "") or raw.get("jobDescription", "")

        return {
            "title": title,
            "company": company,
            "location": raw.get("location", search_location),
            "remote_type": raw.get("workplaceType", "") or raw.get("remoteType", ""),
            "url": url,
            "description": _strip_html(description),
            "posted_at": posted_at,
            "search_keyword": search_keyword,
            "search_location": search_location,
            "salary": raw.get("salary", "") or raw.get("salarySpecified", ""),
        }
    except Exception as e:
        logger.error("Job normalization failed: %s", e)
        return None


def _parse_relative_date(text: str) -> datetime | None:
    """Parse relative date strings like '2 hours ago', '1 day ago'."""
    now = datetime.utcnow()
    text = text.lower().strip()

    try:
        if "just now" in text or "moment" in text:
            return now
        if "hour" in text:
            hours = int("".join(c for c in text.split("hour")[0] if c.isdigit()) or "1")
            return now - timedelta(hours=hours)
        if "day" in text:
            days = int("".join(c for c in text.split("day")[0] if c.isdigit()) or "1")
            return now - timedelta(days=days)
        if "minute" in text:
            minutes = int(
                "".join(c for c in text.split("minute")[0] if c.isdigit()) or "1"
            )
            return now - timedelta(minutes=minutes)
        if "week" in text:
            weeks = int("".join(c for c in text.split("week")[0] if c.isdigit()) or "1")
            return now - timedelta(weeks=weeks)
        if "month" in text:
            months = int(
                "".join(c for c in text.split("month")[0] if c.isdigit()) or "1"
            )
            return now - timedelta(days=months * 30)
    except (ValueError, IndexError):
        pass

    # Try ISO format
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def _strip_html(text: str) -> str:
    """Simple HTML tag removal."""
    import re

    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean
