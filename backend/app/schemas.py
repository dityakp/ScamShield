"""
Pydantic request / response schemas for ScamShield API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RegisterResponse(BaseModel):
    message: str
    user: UserOut


class MessageResponse(BaseModel):
    message: str


# ── Scan / Predict ────────────────────────────────────────────

class PredictRequest(BaseModel):
    type: str = Field(..., pattern=r"^(message|url|other)$")
    text: str = Field(..., min_length=10, max_length=5000)


class PredictResponse(BaseModel):
    risk_level: str
    risk_score: float
    explanation: str
    indicators: List[str]
    type: str
    created_at: datetime
    precaution: Optional[str] = None  # xAI-generated safety advice

    class Config:
        from_attributes = True


class ScanHistoryItem(BaseModel):
    date: str
    type: str
    snippet: str
    risk: str
    score: float

    class Config:
        from_attributes = True


# ── Reports ───────────────────────────────────────────────────

class ReportRequest(BaseModel):
    scam_type: str = Field(..., min_length=1, max_length=100)
    channel: Optional[str] = Field(None, max_length=100)
    identifier: Optional[str] = Field(None, max_length=500)
    description: str = Field(..., min_length=20, max_length=5000)


class ReportResponse(BaseModel):
    message: str
    report_id: int


class ReportHistoryItem(BaseModel):
    type: str
    channel: str
    when: str


# ── Dashboard ─────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_scans: int
    high_risk_count: int
    total_reports: int
    recent_scans: List[ScanHistoryItem]
    recent_reports: List[ReportHistoryItem]
