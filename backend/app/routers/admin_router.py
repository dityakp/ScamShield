"""
Admin router – /api/admin/*
All endpoints require a valid JWT from a user with is_admin == True.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, ScanResult, ScamReport
from app.schemas import (
    AdminLoginRequest,
    AdminTokenResponse,
    AdminUserItem,
    AdminScanItem,
    AdminReportItem,
    AdminStats,
    MessageResponse,
    UserOut,
)
from app.auth import verify_password, create_access_token
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Admin Login ───────────────────────────────────────────────

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(body: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate as admin. Returns a JWT only if the user has is_admin == True.
    Deliberately returns the same error message whether the email doesn't exist
    or the user is not an admin (to avoid information leakage).
    """
    user = db.query(User).filter(User.email == body.email).first()

    # Verify password and admin flag — same error message for both failures
    if not user or not verify_password(body.password, user.password_hash) or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or insufficient permissions.",
        )

    token = create_access_token({"sub": str(user.id)})
    return AdminTokenResponse(
        access_token=token,
        admin=UserOut.model_validate(user),
    )


# ── Platform Stats ────────────────────────────────────────────

@router.get("/stats", response_model=AdminStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return platform-wide aggregate statistics."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    total_users = db.query(func.count(User.id)).scalar()
    total_scans = db.query(func.count(ScanResult.id)).scalar()
    total_reports = db.query(func.count(ScamReport.id)).scalar()

    high_risk = db.query(func.count(ScanResult.id)).filter(ScanResult.risk_level == "High").scalar()
    medium_risk = db.query(func.count(ScanResult.id)).filter(ScanResult.risk_level == "Medium").scalar()
    low_risk = db.query(func.count(ScanResult.id)).filter(ScanResult.risk_level == "Low").scalar()

    scans_today = (
        db.query(func.count(ScanResult.id))
        .filter(ScanResult.created_at >= today_start)
        .scalar()
    )
    reports_today = (
        db.query(func.count(ScamReport.id))
        .filter(ScamReport.created_at >= today_start)
        .scalar()
    )
    new_users_today = (
        db.query(func.count(User.id))
        .filter(User.created_at >= today_start)
        .scalar()
    )

    return AdminStats(
        total_users=total_users,
        total_scans=total_scans,
        total_reports=total_reports,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        scans_today=scans_today,
        reports_today=reports_today,
        new_users_today=new_users_today,
    )


# ── User Management ───────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserItem])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return all registered users with scan/report counts."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        result.append(AdminUserItem(
            id=u.id,
            name=u.name,
            email=u.email,
            is_admin=u.is_admin,
            is_active=u.is_active,
            created_at=u.created_at,
            scan_count=len(u.scans),
            report_count=len(u.reports),
        ))
    return result


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete a user and all their data. Cannot delete yourself."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account.",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    db.delete(user)
    db.commit()
    return MessageResponse(message=f"User '{user.email}' deleted successfully.")


@router.patch("/users/{user_id}/toggle-admin", response_model=MessageResponse)
def toggle_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Grant or revoke admin privileges for a user."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own admin status.",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_admin = not user.is_admin
    db.commit()
    action = "granted" if user.is_admin else "revoked"
    return MessageResponse(message=f"Admin access {action} for '{user.email}'.")


@router.patch("/users/{user_id}/toggle-active", response_model=MessageResponse)
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Activate or deactivate a user account."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = not user.is_active
    db.commit()
    action = "activated" if user.is_active else "deactivated"
    return MessageResponse(message=f"User '{user.email}' {action}.")


# ── Scan Management ───────────────────────────────────────────

@router.get("/scans", response_model=list[AdminScanItem])
def list_all_scans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return all scans across all users, newest first."""
    scans = (
        db.query(ScanResult)
        .order_by(ScanResult.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for s in scans:
        result.append(AdminScanItem(
            id=s.id,
            user_id=s.user_id,
            user_email=s.user.email if s.user else "deleted",
            scan_type=s.scan_type,
            snippet=s.input_text[:80] + ("…" if len(s.input_text) > 80 else ""),
            risk_level=s.risk_level,
            risk_score=round(s.risk_score, 1),
            created_at=s.created_at,
        ))
    return result


# ── Report Management ─────────────────────────────────────────

@router.get("/reports", response_model=list[AdminReportItem])
def list_all_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Return all scam reports across all users, newest first."""
    reports = (
        db.query(ScamReport)
        .order_by(ScamReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for r in reports:
        result.append(AdminReportItem(
            id=r.id,
            user_id=r.user_id,
            user_email=r.user.email if r.user else "deleted",
            scam_type=r.scam_type,
            channel=r.channel,
            identifier=r.identifier,
            description=r.description,
            created_at=r.created_at,
        ))
    return result


@router.delete("/reports/{report_id}", response_model=MessageResponse)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Delete a specific scam report."""
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    db.delete(report)
    db.commit()
    return MessageResponse(message=f"Report #{report_id} deleted.")
