from __future__ import annotations

import json

from app.models import Job, JobStatus


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestResumeUpload:
    def test_upload_unsupported_format(self, client):
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.exe", b"binary", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_txt_resume(self, client, tmp_path):
        resume_content = b"John Doe\nDevOps Engineer\nAWS, Kubernetes, Terraform"
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.txt", resume_content, "text/plain")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "profile_id" in data


class TestJobsEndpoint:
    def test_list_jobs_empty(self, client):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["jobs"] == []

    def test_get_nonexistent_job(self, client):
        response = client.get("/api/jobs/9999")
        assert response.status_code == 404


class TestApplicationsEndpoint:
    def test_list_applications_empty(self, client):
        response = client.get("/api/applications")
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_approve_nonexistent(self, client):
        response = client.post("/api/applications/9999/approve")
        assert response.status_code == 404

    def test_cancel_nonexistent(self, client):
        response = client.post("/api/applications/9999/cancel")
        assert response.status_code == 404


class TestDashboardEndpoint:
    def test_dashboard_empty(self, client):
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 0
        assert data["strong_matches"] == 0


class TestExportEndpoint:
    def test_export_csv(self, client):
        response = client.get("/api/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_excel(self, client):
        response = client.get("/api/export/excel")
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
