"""
ScamShield Backend - FastAPI application entry point.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.routers import auth_router, scan_router, report_router, dashboard_router, admin_router

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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routers (must come before catch-all) ─────────
app.include_router(auth_router.router)
app.include_router(scan_router.router)
app.include_router(report_router.router)
app.include_router(dashboard_router.router)
app.include_router(admin_router.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ScamShield API", "version": "1.0.0"}


# ── Frontend static file serving ──────────────────────────────
# Resolve the assets directory relative to this file:
# backend/app/main.py  ->  ../../assets  ->  ScamShield/assets
_assets_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "assets")
)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    """
    Catch-all GET route that serves files from the assets/ directory.
    Registered AFTER all API routers, so /api/* routes always win.
    POST/PUT/DELETE requests to /api/* are never affected.
    """
    # Strip leading slash just in case
    full_path = full_path.lstrip("/")

    # Detect if it's a known static asset folder
    is_static = any(full_path.startswith(prefix) for prefix in ["css/", "js/", "images/"])

    # Bare root -> index.html
    if not full_path:
        target = os.path.join(_assets_dir, "html", "index.html")
    elif is_static:
        target = os.path.join(_assets_dir, full_path)
    else:
        target = os.path.join(_assets_dir, "html", full_path)

    # Security: prevent directory traversal
    target = os.path.abspath(target)
    if not target.startswith(_assets_dir):
        return HTMLResponse("Not found", status_code=404)

    # Exact file match (html, css, js, images, etc.)
    if os.path.isfile(target):
        return FileResponse(target)

    # Try .html extension (e.g. /admin-login -> html/admin-login.html)
    if not is_static and os.path.isfile(target + ".html"):
        return FileResponse(target + ".html")

    # Fallback to index.html
    fallback = os.path.join(_assets_dir, "html", "index.html")
    if os.path.isfile(fallback):
        return FileResponse(fallback)

    return HTMLResponse("Not found", status_code=404)
