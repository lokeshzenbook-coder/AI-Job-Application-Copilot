from __future__ import annotations

import logging
from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.excel_export import export_jobs_to_csv, export_jobs_to_xlsx

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/excel")
def export_excel(db: Session = Depends(get_db)):
    xlsx_bytes = export_jobs_to_xlsx(db)
    return StreamingResponse(
        BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=job_matches.xlsx"},
    )


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    csv_content = export_jobs_to_csv(db)
    return StreamingResponse(
        BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=job_matches.csv"},
    )
