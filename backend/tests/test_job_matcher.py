from __future__ import annotations

from datetime import datetime, timedelta

from app.services.job_matcher import filter_recent_jobs


class TestFilterRecentJobs:
    def test_keeps_recent_jobs(self):
        jobs = [
            {
                "title": "DevOps Engineer",
                "company": "A",
                "url": "http://a.com",
                "posted_at": datetime.utcnow() - timedelta(hours=2),
            },
            {
                "title": "SRE",
                "company": "B",
                "url": "http://b.com",
                "posted_at": datetime.utcnow() - timedelta(hours=12),
            },
        ]
        result = filter_recent_jobs(jobs, hours=24)
        assert len(result) == 2

    def test_filters_old_jobs(self):
        jobs = [
            {
                "title": "Old Job",
                "company": "A",
                "url": "http://a.com",
                "posted_at": datetime.utcnow() - timedelta(hours=48),
            },
        ]
        result = filter_recent_jobs(jobs, hours=24)
        assert len(result) == 0

    def test_keeps_unknown_posting_date(self):
        jobs = [
            {
                "title": "Unknown Date Job",
                "company": "A",
                "url": "http://a.com",
                "posted_at": None,
            },
        ]
        result = filter_recent_jobs(jobs, hours=24)
        assert len(result) == 1

    def test_boundary_just_under_24h(self):
        jobs = [
            {
                "title": "Just under 24h",
                "company": "A",
                "url": "http://a.com",
                "posted_at": datetime.utcnow() - timedelta(hours=23, minutes=59),
            },
        ]
        result = filter_recent_jobs(jobs, hours=24)
        assert len(result) == 1
