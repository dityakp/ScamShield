"""
ScamShield Backend – FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.routers import auth_router, scan_router, report_router, dashboard_router

# ── Create all tables ─────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Rate limiter ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="ScamShield API",
    description="AI-based scam detection & public reporting backend.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ─────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(scan_router.router)
app.include_router(report_router.router)
app.include_router(dashboard_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ScamShield API", "version": "1.0.0"}
