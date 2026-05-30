from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
CORAL_QUERY = "SELECT id, title, description, url FROM devto_agent.articles LIMIT 15"


def _sample_articles() -> list[dict[str, Any]]:
    """High-signal demo data that keeps the dashboard useful even without Coral."""
    return [
        {
            "id": 1001,
            "title": "Shipping a secure API gateway with FastAPI",
            "description": "A practical guide to auth, rate limits, and observability for developer platforms.",
            "url": "https://dev.to/"
        },
        {
            "id": 1002,
            "title": "Urgent: claim a free AI token airdrop now",
            "description": "Connect your wallet, verify your seed phrase, and receive rewards instantly.",
            "url": "https://dev.to/"
        },
        {
            "id": 1003,
            "title": "How to protect API keys in CI pipelines",
            "description": "Use secrets managers and short-lived tokens to avoid accidental leaks.",
            "url": "https://dev.to/"
        },
        {
            "id": 1004,
            "title": "NEW: npm package that fixes everything in one command",
            "description": "Run curl | bash to install the maintainer's trusted optimization script.",
            "url": "https://dev.to/"
        },
        {
            "id": 1005,
            "title": "React performance tips for large dashboards",
            "description": "Memoization, virtualization, and careful state design reduce rendering overhead.",
            "url": "https://dev.to/"
        },
        {
            "id": 1006,
            "title": "My email, phone number, and address are in this bug report",
            "description": "The pasted screenshot includes full contact details and environment variables.",
            "url": "https://dev.to/"
        },
        {
            "id": 1007,
            "title": "Open source security checklist for solo founders",
            "description": "Dependency pinning, SCA scanning, and safe defaults before launch.",
            "url": "https://dev.to/"
        },
        {
            "id": 1008,
            "title": "Get verified instantly with this free gift card trick",
            "description": "Limited offer, act now, confirm your password reset link, and avoid missing out.",
            "url": "https://dev.to/"
        },
        {
            "id": 1009,
            "title": "A gentle intro to Docker networking",
            "description": "Bridge, host, and overlay networking explained with diagrams and examples.",
            "url": "https://dev.to/"
        },
        {
            "id": 1010,
            "title": "This crypto tool prints your wallet balance and private key",
            "description": "The utility requests seed phrases so you can unlock hidden analytics.",
            "url": "https://dev.to/"
        },
        {
            "id": 1011,
            "title": "How I built a moderation queue with SQLite",
            "description": "The article covers queue design, triage labels, and reviewer workflows.",
            "url": "https://dev.to/"
        },
        {
            "id": 1012,
            "title": "Please roast my code, I'm terrible at this",
            "description": "The tone is abusive and targeted harassment in the discussion thread.",
            "url": "https://dev.to/"
        },
    ]


def fetch_devto_data(source_mode: str = "Coral SQL") -> list[dict[str, Any]]:
    """
    Pull Dev.to articles through Coral.
    Falls back to bundled demo rows if Coral is missing or the source is offline.
    """
    if source_mode == "Demo fallback":
        return _sample_articles()

    try:
        result = subprocess.run(
            ["coral", "sql", CORAL_QUERY, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout.strip() or "[]")
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            # Some Coral setups wrap rows in a top-level object.
            for key in ("rows", "data", "result"):
                if key in payload and isinstance(payload[key], list):
                    return payload[key]
        return _sample_articles()
    except Exception:
        return _sample_articles()


def _classify_with_llm(title: str, description: str, scan_mode: str) -> dict[str, Any] | None:
    """
    Optional LLM path.
    Uses OpenAI or Gemini only when credentials exist and the SDK is installed.
    Any import or provider failure returns None so the heuristic engine can take over.
    """
    prompt = f"""
You are an expert developer-community security moderator.

Task:
Classify the content into one of these risk levels:
- HIGH
- MEDIUM
- LOW

Pick exactly one violation type:
- Malicious Package
- Phishing/Scam
- PII Leak
- Harassment
- Clickbait
- None

Context:
Scan mode: {scan_mode}
Title: {title}
Description: {description}

Return a strict JSON object with:
{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "violation_type": "Malicious Package|Phishing/Scam|PII Leak|Harassment|Clickbait|None",
  "summary": "brief explanation",
  "confidence": 0.0
}}
"""

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI  # type: ignore

            model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            text = response.choices[0].message.content or ""
            return json.loads(text)
        except Exception:
            pass

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai  # type: ignore

            model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            return json.loads(text)
        except Exception:
            pass

    return None


def _heuristic_scan(title: str, description: str, scan_mode: str) -> dict[str, Any]:
    """
    Deterministic fallback that still produces useful moderation output offline.
    """
    text = f"{title} {description}".lower()
    signals: list[str] = []

    keyword_groups = {
        "Malicious Package": [
            "npm install", "pip install", "curl | bash", "one command", "backdoor",
            "supply chain", "typosquat", "dependency confusion", "malware", "trojan",
            "package", "installer"
        ],
        "Phishing/Scam": [
            "airdrop", "free token", "wallet", "seed phrase", "verify your account",
            "claim now", "limited offer", "urgent", "gift card", "password reset", "crypto"
        ],
        "PII Leak": [
            "email", "phone number", "address", "api key", "secret", "password",
            "token", "private key", "screenshot", "personal data"
        ],
        "Harassment": [
            "dox", "doxx", "roast my code", "you're terrible", "abusive", "insult"
        ],
        "Clickbait": [
            "shocking", "won't believe", "new:", "urgent:", "best ever", "click here",
            "free", "limited offer", "instantly", "secret"
        ],
    }

    scan_priority = {
        "Malicious Packages": {"Malicious Package"},
        "Phishing & Scams": {"Phishing/Scam", "Clickbait"},
        "PII Leak": {"PII Leak"},
        "All Threats": set(keyword_groups.keys()),
    }.get(scan_mode, set(keyword_groups.keys()))

    detected = []
    for violation_type, words in keyword_groups.items():
        if violation_type not in scan_priority:
            continue
        for word in words:
            if word in text:
                signals.append(word)
                detected.append(violation_type)

    # Decide final risk level.
    if "PII Leak" in detected or ("Malicious Package" in detected and "Phishing/Scam" in detected):
        risk_level = "HIGH"
    elif len(detected) >= 2:
        risk_level = "HIGH"
    elif detected:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    violation_type = detected[0] if detected else "None"
    if risk_level == "LOW":
        summary = "No strong moderation risk signal found."
        confidence = 0.94
    elif risk_level == "MEDIUM":
        summary = f"Potential {violation_type.lower()} indicators detected: {', '.join(signals[:3])}."
        confidence = 0.82
    else:
        summary = f"Multiple risk signals detected: {', '.join(signals[:4])}."
        confidence = 0.91

    # Slightly sharpen the signal when the mode is specific.
    if scan_mode != "All Threats" and violation_type == "None" and signals:
        violation_type = detected[0]

    return {
        "risk_level": risk_level,
        "violation_type": violation_type,
        "summary": summary,
        "confidence": confidence,
        "signals": signals[:6],
    }


def scan_post_content(title: str, description: str, scan_mode: str = "All Threats") -> dict[str, Any]:
    """
    Analyze one article and return moderation metadata.
    Uses LLMs when available; otherwise falls back to a strong heuristic engine.
    """
    llm_result = _classify_with_llm(title, description, scan_mode)
    if isinstance(llm_result, dict) and llm_result:
        # Normalize expected keys.
        return {
            "risk_level": str(llm_result.get("risk_level", "LOW")).upper(),
            "violation_type": llm_result.get("violation_type", "None"),
            "summary": llm_result.get("summary", "Analysis complete."),
            "confidence": float(llm_result.get("confidence", 0.78) or 0.78),
            "signals": [],
        }

    return _heuristic_scan(title, description, scan_mode)
