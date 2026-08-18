from __future__ import annotations

from app.services.dedup import (
    deduplicate_jobs,
    generate_job_fingerprint,
    is_duplicate,
    is_fuzzy_duplicate,
    normalize_for_dedup,
)


class TestFingerprint:
    def test_same_jobs_same_fingerprint(self):
        fp1 = generate_job_fingerprint("DevOps Engineer", "Google", "http://google.com/jobs/1")
        fp2 = generate_job_fingerprint("DevOps Engineer", "Google", "http://google.com/jobs/1")
        assert fp1 == fp2

    def test_different_jobs_different_fingerprint(self):
        fp1 = generate_job_fingerprint("DevOps Engineer", "Google", "http://google.com/jobs/1")
        fp2 = generate_job_fingerprint("DevOps Engineer", "Meta", "http://meta.com/jobs/1")
        assert fp1 != fp2

    def test_case_insensitive(self):
        fp1 = generate_job_fingerprint("DevOps Engineer", "Google", "http://google.com/jobs/1")
        fp2 = generate_job_fingerprint("devops engineer", "google", "http://google.com/jobs/1")
        assert fp1 == fp2


class TestNormalizeForDedup:
    def test_removes_senior(self):
        assert normalize_for_dedup("Senior DevOps Engineer") == normalize_for_dedup("DevOps Engineer")

    def test_removes_sr(self):
        assert normalize_for_dedup("Sr. DevOps Engineer") == normalize_for_dedup("DevOps Engineer")

    def test_lowercase(self):
        assert normalize_for_dedup("DEVOPS ENGINEER") == "devops engineer"


class TestIsDuplicate:
    def test_exact_duplicate(self):
        job = {"title": "DevOps", "company": "A", "url": "http://a.com"}
        fp = generate_job_fingerprint(job["title"], job["company"], job["url"])
        assert is_duplicate(job, {fp}) is True

    def test_not_duplicate(self):
        job = {"title": "DevOps", "company": "A", "url": "http://a.com"}
        assert is_duplicate(job, set()) is False


class TestFuzzyDuplicate:
    def test_fuzzy_duplicate_same_company(self):
        jobs = [{"title": "Senior DevOps Engineer", "company": "Google"}]
        new_job = {"title": "Sr. DevOps Engineer", "company": "Google"}
        assert is_fuzzy_duplicate(new_job, jobs) is True

    def test_not_fuzzy_different_company(self):
        jobs = [{"title": "Senior DevOps Engineer", "company": "Google"}]
        new_job = {"title": "Sr. DevOps Engineer", "company": "Meta"}
        assert is_fuzzy_duplicate(new_job, jobs) is False

    def test_different_roles_not_duplicate(self):
        jobs = [{"title": "DevOps Engineer", "company": "Google"}]
        new_job = {"title": "Site Reliability Engineer", "company": "Google"}
        assert is_fuzzy_duplicate(new_job, jobs) is False


class TestDeduplicateJobs:
    def test_removes_exact_duplicates(self):
        jobs = [
            {"title": "DevOps", "company": "A", "url": "http://a.com/1"},
            {"title": "DevOps", "company": "A", "url": "http://a.com/1"},
            {"title": "SRE", "company": "B", "url": "http://b.com/1"},
        ]
        result = deduplicate_jobs(jobs)
        assert len(result) == 2

    def test_removes_fuzzy_duplicates(self):
        jobs = [
            {"title": "Senior DevOps Engineer", "company": "A", "url": "http://a.com/1"},
            {"title": "Sr. DevOps Engineer", "company": "A", "url": "http://a.com/2"},
        ]
        result = deduplicate_jobs(jobs)
        assert len(result) == 1

    def test_keeps_different_companies(self):
        jobs = [
            {"title": "DevOps Engineer", "company": "A", "url": "http://a.com/1"},
            {"title": "DevOps Engineer", "company": "B", "url": "http://b.com/1"},
        ]
        result = deduplicate_jobs(jobs)
        assert len(result) == 2
