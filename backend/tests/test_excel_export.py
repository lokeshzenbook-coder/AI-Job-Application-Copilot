from __future__ import annotations

import json

from app.models import Application, Job, JobStatus
from app.services.excel_export import export_jobs_to_csv, export_jobs_to_xlsx


class TestExcelExport:
    def test_xlsx_export_empty(self, db_session):
        result = export_jobs_to_xlsx(db_session)
        assert isinstance(result, bytes)
        assert len(result) > 0  # Should at least produce an empty workbook

    def test_csv_export_empty(self, db_session):
        result = export_jobs_to_csv(db_session)
        assert isinstance(result, str)
        assert "Rank" in result  # Headers should be present

    def test_xlsx_export_with_jobs(self, db_session):
        job = Job(
            company="TestCorp",
            title="DevOps Engineer",
            location="Remote",
            url="http://test.com/jobs/1",
            description="Test JD",
            match_score=92.0,
            interview_probability="HIGH",
            recommendation="APPLY",
            status=JobStatus.MATCHED.value,
        )
        db_session.add(job)
        db_session.commit()

        result = export_jobs_to_xlsx(db_session)
        assert len(result) > 0

        # Verify CSV also works
        csv_result = export_jobs_to_csv(db_session)
        assert "TestCorp" in csv_result
        assert "DevOps Engineer" in csv_result
