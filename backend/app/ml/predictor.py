"""
ML predictor – loads a trained model or falls back to rule-based scoring.
"""

import os
import re
from pathlib import Path
from datetime import datetime, timezone

import joblib

_MODEL_DIR = Path(__file__).parent / "data"
_MODEL_PATH = _MODEL_DIR / "model.joblib"
_VECTORIZER_PATH = _MODEL_DIR / "vectorizer.joblib"

# Lazy-loaded model + vectorizer
_model = None
_vectorizer = None


def _load_model():
    """Try to load persisted ML model; return (model, vectorizer) or (None, None)."""
    global _model, _vectorizer
    if _model is not None:
        return _model, _vectorizer
    if _MODEL_PATH.exists() and _VECTORIZER_PATH.exists():
        _model = joblib.load(_MODEL_PATH)
        _vectorizer = joblib.load(_VECTORIZER_PATH)
    return _model, _vectorizer


# ── Keyword-based indicator extraction ────────────────────────

_INDICATOR_RULES = [
    (["kyc", "account suspension", "verification", "verify"],       "KYC / verification pressure"),
    (["otp", "one time password", "one-time password"],             "OTP harvesting attempt"),
    (["click", "tap", "click here", "tap here"],                    "Call-to-action clickbait"),
    (["lottery", "prize", "winner", "won", "congratulations"],      "Unsolicited reward / lottery"),
    (["upi", "imps", "rtgs", "bank transfer", "neft"],             "UPI / bank transfer request"),
    (["urgent", "immediately", "asap", "within 24 hours", "hurry"],"Urgency / time pressure"),
    (["password", "pin", "cvv", "card number"],                     "Credential harvesting"),
    (["investment", "trading", "guaranteed return", "double money"],"Investment / Ponzi scam"),
    (["customer support", "customer care", "helpline"],             "Fake customer support"),
]


def _extract_indicators(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for keywords, label in _INDICATOR_RULES:
        if any(kw in lowered for kw in keywords):
            found.append(label)
    return found


# ── Explanation generator ─────────────────────────────────────

def _generate_explanation(level: str, indicators: list[str]) -> str:
    if level == "High":
        return (
            "Multiple high-risk patterns detected including "
            + ", ".join(indicators[:3]).lower()
            + ". This content strongly resembles known scam templates."
        )
    if level == "Medium":
        return (
            "Some scam-like indicators found ("
            + ", ".join(indicators[:2]).lower()
            + "). Users should independently verify using official channels."
        )
    return (
        "Limited scam markers detected. The content appears relatively safe, "
        "but users should still avoid sharing OTPs, passwords or PINs."
    )


# ── Rule-based fallback scorer ────────────────────────────────

def _rule_based_score(text: str, indicators: list[str]) -> float:
    base = min(95, max(5, round(len(text) / 4)))
    if len(indicators) >= 4:
        base = max(base, 88)
    elif len(indicators) >= 3:
        base = max(base, 78)
    elif len(indicators) == 2:
        base = max(base, 58)
    elif len(indicators) == 1:
        base = max(base, 42)
    return float(base)


# ── Public prediction function ────────────────────────────────

def predict_risk(text: str, scan_type: str) -> dict:
    """
    Return a prediction dict:
    { risk_level, risk_score, explanation, indicators, type, created_at }
    """
    indicators = _extract_indicators(text)

    model, vectorizer = _load_model()
    if model is not None and vectorizer is not None:
        # ML-based prediction
        features = vectorizer.transform([text])
        proba = model.predict_proba(features)[0]  # [safe_prob, scam_prob]
        scam_prob = float(proba[1]) * 100
        risk_score = round(min(99, max(1, scam_prob)), 1)
    else:
        # Fallback to rule-based
        risk_score = _rule_based_score(text, indicators)

    if risk_score >= 75:
        risk_level = "High"
    elif risk_score >= 45:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    explanation = _generate_explanation(risk_level, indicators)

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "explanation": explanation,
        "indicators": indicators,
        "type": scan_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Utility for human-friendly time deltas ────────────────────

def _humanize_timedelta(now: datetime, then: datetime) -> str:
    """Convert a datetime delta into a short human string like 'Today · 10:20'."""
    diff = now - then
    time_str = then.strftime("%H:%M")

    if diff.days == 0:
        return f"Today · {time_str}"
    elif diff.days == 1:
        return f"Yesterday · {time_str}"
    elif diff.days < 7:
        return f"{diff.days} days ago · {time_str}"
    else:
        return then.strftime("%Y-%m-%d · %H:%M")
