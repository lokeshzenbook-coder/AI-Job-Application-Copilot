from __future__ import annotations

import pytest

from app.models import Application, Job, JobStatus


class TestPlaywrightFormFill:
    def test_fill_form_no_application(self, client):
        response = client.post("/api/applications/9999/fill-form")
        assert response.status_code == 404

    def test_fill_form_no_resume(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/apply",
            description="JD",
        )
        db_session.add(job)
        db_session.commit()

        app = Application(job_id=job.id, status=JobStatus.QUEUED.value)
        db_session.add(app)
        db_session.commit()

        response = client.post(f"/api/applications/{app.id}/fill-form")
        assert response.status_code == 400


class TestHumanApprovalGate:
    def test_cannot_submit_without_approval(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/apply",
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

        response = client.post(f"/api/applications/{app.id}/submit")
        assert response.status_code == 400
        assert "must be SUBMITTED" in response.json()["detail"]

    def test_submit_after_approval(self, client, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            url="http://test.com/apply",
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

        # Approve first
        approve_resp = client.post(f"/api/applications/{app.id}/approve")
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == "SUBMITTED"

        # Now submit is allowed (returns manual submission instruction)
        submit_resp = client.post(f"/api/applications/{app.id}/submit")
        assert submit_resp.status_code == 200
        assert "manually" in submit_resp.json()["message"].lower()
