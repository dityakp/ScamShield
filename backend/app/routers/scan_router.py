"""
Scan router – /api/predict, /api/history
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ScanResult
from app.schemas import PredictRequest, PredictResponse, ScanHistoryItem
from app.dependencies import get_current_user
from app.ml.predictor import predict_risk
from app.ml.gemini_advisor import get_precaution_advice

router = APIRouter(prefix="/api", tags=["Scan & Predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Run the ML risk engine on the supplied text and persist the result.
    """
    try:
        result = predict_risk(body.text, body.type)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"ML Prediction Error: {str(e)}")

    # ── Generate Gemini precautionary advice ─────────────────────
    precaution = get_precaution_advice(
        text=body.text,
        scan_type=body.type,
        risk_level=result["risk_level"],
        indicators=result["indicators"],
    )

    scan = ScanResult(
        user_id=current_user.id,
        scan_type=body.type,
        input_text=body.text,
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        explanation=result["explanation"],
        indicators=result["indicators"],
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return PredictResponse(
        risk_level=scan.risk_level,
        risk_score=scan.risk_score,
        explanation=scan.explanation,
        indicators=scan.indicators,
        type=scan.scan_type,
        created_at=scan.created_at,
        precaution=precaution,
    )


@router.get("/history", response_model=list[ScanHistoryItem])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Return the current user's scan history, newest first.
    """
    scans = (
        db.query(ScanResult)
        .filter(ScanResult.user_id == current_user.id)
        .order_by(ScanResult.created_at.desc())
        .limit(50)
        .all()
    )

    items = []
    for s in scans:
        snippet = s.input_text[:80] + ("…" if len(s.input_text) > 80 else "")
        items.append(
            ScanHistoryItem(
                date=s.created_at.strftime("%Y-%m-%d %H:%M"),
                type=s.scan_type.capitalize(),
                snippet=snippet,
                risk=s.risk_level,
                score=s.risk_score,
            )
        )

    return items
