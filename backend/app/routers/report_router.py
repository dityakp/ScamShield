"""
Report router – /api/report (POST to submit, GET to list)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ScamReport
from app.schemas import ReportRequest, ReportResponse, ReportHistoryItem, MessageResponse
from app.dependencies import get_current_user
from app.ml.predictor import _humanize_timedelta

from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Reports"])


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    body: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a new scam report."""
    report = ScamReport(
        user_id=current_user.id,
        scam_type=body.scam_type,
        channel=body.channel or "",
        identifier=body.identifier or "",
        description=body.description,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(message="Scam report submitted successfully.", report_id=report.id)


@router.get("/report", response_model=list[ReportHistoryItem])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the current user's report history, newest first."""
    reports = (
        db.query(ScamReport)
        .filter(ScamReport.user_id == current_user.id)
        .order_by(ScamReport.created_at.desc())
        .limit(50)
        .all()
    )

    items = []
    now = datetime.now(timezone.utc)
    for r in reports:
        items.append(
            ReportHistoryItem(
                type=r.scam_type,
                channel=r.channel or "N/A",
                when=_humanize_timedelta(now, r.created_at),
            )
        )

    return items
