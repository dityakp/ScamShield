"""
Google Gemini advisor – generates human-friendly precautionary advice
when a scam or suspicious content is detected by the ML model.
Falls back to built-in advice when the API is unavailable.
"""

import json
import logging
from typing import Optional

import requests

from app.config import settings

_MODEL = "gemini-2.5-flash"
_GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{_MODEL}:generateContent"

_log = logging.getLogger(__name__)


# ── Built-in fallback advice (when Gemini API is unavailable) ────
_FALLBACK_ADVICE = {
    "High": (
        "1. Do NOT click any links or download attachments from this message.\n"
        "2. Do NOT share any personal information, OTPs, passwords, or bank details.\n"
        "3. Block the sender immediately and report them to your email/SMS provider.\n"
        "4. If you have already shared sensitive info, contact your bank and change your passwords immediately.\n"
        "5. Report this scam to your local cybercrime helpline or portal."
    ),
    "Medium": (
        "1. Be cautious — do not click any links until you independently verify the sender.\n"
        "2. Cross-check any claims by visiting the official website directly (not via links in the message).\n"
        "3. Never share OTPs, passwords, or financial details in response to unsolicited messages.\n"
        "4. If something feels off, trust your instincts and ignore the message.\n"
        "5. Consider reporting the message to your service provider as suspicious."
    ),
    "Low": (
        "1. The content appears relatively safe, but stay cautious with unsolicited messages.\n"
        "2. Avoid sharing personal or financial information unless you initiated the contact.\n"
        "3. Verify the sender's identity through official channels if in doubt.\n"
        "4. Keep your devices and passwords updated to stay protected."
    ),
}


def _build_prompt(text: str, scan_type: str, risk_level: str, indicators: list[str]) -> str:
    indicator_str = ", ".join(indicators) if indicators else "none identified"
    return (
        f"A user submitted the following {scan_type} content to be checked for scams:\n\n"
        f'"""\n{text}\n"""\n\n'
        f"The AI risk engine classified it as **{risk_level} risk** "
        f"with these scam indicators: {indicator_str}.\n\n"
        "Your role is a cybersecurity advisor at ScamShield. "
        "Provide clear, concise, actionable precautions the user should take RIGHT NOW. "
        "CRITICAL: You MUST specifically mention the exact details from the user's message (e.g., the specific company name, the exact amount of money promised like '₹25,000', or the specific suspicious URL) in your advice to prove this is a custom analysis. "
        "Format your response as a short numbered list (3-5 points). "
        "If risk is Low, still give gentle safety reminders. "
        "Keep each point on one line. Do NOT include markdown headers or bold text, just the numbered list."
    )


def get_precaution_advice(
    text: str,
    scan_type: str,
    risk_level: str,
    indicators: list[str],
) -> Optional[str]:
    """
    Call Google Gemini API and return a precautionary advice string.
    Falls back to built-in advice if the API is unavailable.
    """
    api_key = settings.GEMINI_API_KEY

    # Guard: reject empty or un-replaced placeholder
    if not api_key or api_key.strip() in ("", "your-gemini-api-key-here"):
        print("[Gemini] ⚠️  GEMINI_API_KEY is not set – using fallback advice.")
        return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])

    print(f"[Gemini] 🔑 Key loaded (last 8 chars: ...{api_key[-8:]})")
    print(f"[Gemini] 📡 Calling {_MODEL} for '{risk_level}' risk scan...")

    prompt = _build_prompt(text, scan_type, risk_level, indicators)

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are ScamShield's cybersecurity precaution advisor. "
                        "Always respond in plain English with a numbered list of practical safety steps. "
                        "Be concise, empathetic, and avoid technical jargon."
                    )
                }
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 400,
            "temperature": 0.4
        }
    }

    try:
        url = f"{_GEMINI_API_URL}?key={api_key}"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )

        if resp.status_code == 200:
            body = resp.json()
            try:
                advice = body["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"[Gemini] ✅ Responded ({len(advice)} chars): {advice[:80]}...")
                return advice
            except (KeyError, IndexError) as err:
                print(f"[Gemini] ❌ Could not parse response correctly: {err}")
                return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])
        else:
            print(f"[Gemini] ❌ HTTP {resp.status_code}: {resp.text[:200]}")
            print("[Gemini] ↩️  Using fallback advice instead.")
            _log.warning("Gemini HTTP %s: %s", resp.status_code, resp.text[:200])
            return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])

    except requests.RequestException as exc:
        print(f"[Gemini] ❌ Request failed: {exc}")
        print("[Gemini] ↩️  Using fallback advice instead.")
        _log.warning("Gemini request failed: %s", exc)
        return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])
