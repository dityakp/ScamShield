"""
xAI (Grok) advisor – generates human-friendly precautionary advice
when a scam or suspicious content is detected by the ML model.
Falls back to built-in advice when the API is unavailable.
"""

import json
import logging
from typing import Optional

import requests

from app.config import settings

_XAI_CHAT_URL = "https://api.x.ai/v1/chat/completions"
_MODEL = "grok-3-mini"
_log = logging.getLogger(__name__)


# ── Built-in fallback advice (when xAI API is unavailable) ────
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
        "Format your response as a short numbered list (3-5 points). "
        "If risk is Low, still give gentle safety reminders. "
        "Keep each point on one line. Do NOT include markdown headers, just the numbered list."
    )


def get_precaution_advice(
    text: str,
    scan_type: str,
    risk_level: str,
    indicators: list[str],
) -> Optional[str]:
    """
    Call xAI Grok API and return a precautionary advice string.
    Falls back to built-in advice if the API is unavailable.
    """
    api_key = settings.XAI_API_KEY

    # Guard: reject empty or un-replaced placeholder
    if not api_key or api_key.strip() in ("", "your-xai-api-key-here"):
        print("[xAI] ⚠️  XAI_API_KEY is not set – using fallback advice.")
        return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])

    print(f"[xAI] 🔑 Key loaded (last 8 chars: ...{api_key[-8:]})")
    print(f"[xAI] 📡 Calling {_MODEL} for '{risk_level}' risk scan...")

    prompt = _build_prompt(text, scan_type, risk_level, indicators)

    payload = {
        "model": _MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are ScamShield's cybersecurity precaution advisor. "
                    "Always respond in plain English with a numbered list of practical safety steps. "
                    "Be concise, empathetic, and avoid technical jargon."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.4,
    }

    try:
        resp = requests.post(
            _XAI_CHAT_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json=payload,
            timeout=15,
        )

        if resp.status_code == 200:
            body = resp.json()
            advice = body["choices"][0]["message"]["content"].strip()
            print(f"[xAI] ✅ Grok responded ({len(advice)} chars): {advice[:80]}...")
            return advice
        else:
            print(f"[xAI] ❌ HTTP {resp.status_code}: {resp.text[:200]}")
            print("[xAI] ↩️  Using fallback advice instead.")
            _log.warning("xAI HTTP %s: %s", resp.status_code, resp.text[:200])
            return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])

    except requests.RequestException as exc:
        print(f"[xAI] ❌ Request failed: {exc}")
        print("[xAI] ↩️  Using fallback advice instead.")
        _log.warning("xAI request failed: %s", exc)
        return _FALLBACK_ADVICE.get(risk_level, _FALLBACK_ADVICE["Low"])
