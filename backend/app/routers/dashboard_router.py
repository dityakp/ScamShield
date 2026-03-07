"""
Dashboard router – /api/dashboard/stats
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ScanResult, ScamReport
from app.schemas import DashboardStats, ScanHistoryItem, ReportHistoryItem
from app.dependencies import get_current_user
from app.ml.predictor import _humanize_timedelta

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Aggregate stats + recent activity for the logged-in user's dashboard.
    """
    uid = current_user.id

    total_scans = db.query(ScanResult).filter(ScanResult.user_id == uid).count()
    high_risk_count = (
        db.query(ScanResult)
        .filter(ScanResult.user_id == uid, ScanResult.risk_level == "High")
        .count()
    )
    total_reports = db.query(ScamReport).filter(ScamReport.user_id == uid).count()

    # Recent scans (last 5)
    recent_scans_raw = (
        db.query(ScanResult)
        .filter(ScanResult.user_id == uid)
        .order_by(ScanResult.created_at.desc())
        .limit(5)
        .all()
    )
    recent_scans = []
    for s in recent_scans_raw:
        snippet = s.input_text[:80] + ("…" if len(s.input_text) > 80 else "")
        recent_scans.append(
            ScanHistoryItem(
                date=s.created_at.strftime("%Y-%m-%d %H:%M"),
                type=s.scan_type.capitalize(),
                snippet=snippet,
                risk=s.risk_level,
                score=s.risk_score,
            )
        )

    # Recent reports (last 3)
    recent_reports_raw = (
        db.query(ScamReport)
        .filter(ScamReport.user_id == uid)
        .order_by(ScamReport.created_at.desc())
        .limit(3)
        .all()
    )
    now = datetime.now(timezone.utc)
    recent_reports = []
    for r in recent_reports_raw:
        recent_reports.append(
            ReportHistoryItem(
                type=r.scam_type,
                channel=r.channel or "N/A",
                when=_humanize_timedelta(now, r.created_at),
            )
        )

    return DashboardStats(
        total_scans=total_scans,
        high_risk_count=high_risk_count,
        total_reports=total_reports,
        recent_scans=recent_scans,
        recent_reports=recent_reports,
    )
