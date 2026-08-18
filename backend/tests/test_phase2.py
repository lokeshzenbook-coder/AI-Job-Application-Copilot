from __future__ import annotations

import json

from app.models import Application, CandidateProfile, Job, JobStatus


class TestTailorResume:
    def test_tailor_no_resume_text(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            description="Looking for DevOps with AWS experience",
        )
        db_session.add(job)
        db_session.commit()

        profile = CandidateProfile(full_name="Test User", raw_text="")
        db_session.add(profile)
        db_session.commit()

        response = client.post(f"/api/jobs/{job.id}/tailor-resume")
        assert response.status_code == 400

    def test_tailor_no_profile(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            description="JD",
        )
        db_session.add(job)
        db_session.commit()

        response = client.post(f"/api/jobs/{job.id}/tailor-resume")
        assert response.status_code == 400


class TestCoverLetter:
    def test_cover_letter_no_profile(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            description="JD",
        )
        db_session.add(job)
        db_session.commit()

        response = client.post(f"/api/jobs/{job.id}/cover-letter")
        assert response.status_code == 400


class TestApplicationWorkflow:
    def test_prepare_application(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            match_score=90.0,
            status=JobStatus.QUEUED.value,
        )
        db_session.add(job)
        db_session.commit()

        app = Application(
            job_id=job.id,
            status=JobStatus.QUEUED.value,
        )
        db_session.add(app)
        db_session.commit()

        response = client.post(f"/api/applications/{app.id}/prepare")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READY_FOR_REVIEW"

    def test_approve_then_cancel(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            match_score=90.0,
            status=JobStatus.QUEUED.value,
        )
        db_session.add(job)
        db_session.commit()

        app = Application(
            job_id=job.id,
            status=JobStatus.READY_FOR_REVIEW.value,
        )
        db_session.add(app)
        db_session.commit()

        response = client.post(f"/api/applications/{app.id}/approve")
        assert response.status_code == 200
        assert response.json()["status"] == "SUBMITTED"

        response = client.post(f"/api/applications/{app.id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "WITHDRAWN"

    def test_cannot_approve_non_reviewable(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/1",
            status=JobStatus.DISCOVERED.value,
        )
        db_session.add(job)
        db_session.commit()

        app = Application(
            job_id=job.id,
            status=JobStatus.SUBMITTED.value,
        )
        db_session.add(app)
        db_session.commit()

        response = client.post(f"/api/applications/{app.id}/approve")
        assert response.status_code == 400
