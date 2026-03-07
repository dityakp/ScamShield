"""
SQLAlchemy ORM models for ScamShield.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    scans = relationship("ScanResult", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("ScamReport", back_populates="user", cascade="all, delete-orphan")


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scan_type = Column(String(50), nullable=False)          # message | url | other
    input_text = Column(Text, nullable=False)
    risk_level = Column(String(10), nullable=False)         # Low | Medium | High
    risk_score = Column(Float, nullable=False)              # 0 – 100
    explanation = Column(Text, nullable=False)
    indicators = Column(JSON, default=list)                 # list of strings
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    user = relationship("User", back_populates="scans")


class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scam_type = Column(String(100), nullable=False)         # phishing | otp | investment | support | romance | other
    channel = Column(String(100), nullable=True)            # WhatsApp, SMS, email, etc.
    identifier = Column(String(500), nullable=True)         # scam URL / phone / handle
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    user = relationship("User", back_populates="reports")
