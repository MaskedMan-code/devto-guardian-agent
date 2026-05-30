from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .models import RiskLabel


@dataclass
class ScanResult:
    risk_label: RiskLabel
    confidence: float
    rationale: str
    highlights: list[str]


PII_PATTERNS = [
    re.compile(r"\b\d{10}\b"),
    re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b\d{1,5}\s+[A-Za-z0-9. ]+\s+(Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b", re.I),
]

SPAM_PATTERNS = [
    re.compile(r"\bbuy now\b", re.I),
    re.compile(r"\blimited time offer\b", re.I),
    re.compile(r"\bfree followers\b", re.I),
    re.compile(r"\bclick here\b", re.I),
    re.compile(r"\bverify your account\b", re.I),
    re.compile(r"http[s]?://", re.I),
    re.compile(r"\bDM me\b", re.I),
]


def heuristic_scan(title: str, body: str) -> ScanResult:
    text = f"{title}\n{body}".strip()
    highlights: list[str] = []

    pii_hits = [p.pattern for p in PII_PATTERNS if p.search(text)]
    spam_hits = [p.pattern for p in SPAM_PATTERNS if p.search(text)]

    if pii_hits:
        highlights.extend(pii_hits)
        return ScanResult(
            risk_label="PII_LEAK",
            confidence=0.95,
            rationale="Detected personal data markers in title/body.",
            highlights=highlights[:4],
        )

    if spam_hits:
        highlights.extend(spam_hits)
        return ScanResult(
            risk_label="SPAM",
            confidence=0.9,
            rationale="Detected promotional, scammy, or manipulation language.",
            highlights=highlights[:4],
        )

    lowered = text.lower()
    if any(k in lowered for k in ["cringe", "low effort", "bot", "repeated", "off-topic"]):
        return ScanResult(
            risk_label="OTHER",
            confidence=0.62,
            rationale="Low-quality or moderation-relevant pattern detected, but no hard spam/PII signal.",
            highlights=[k for k in ["cringe", "low effort", "bot", "repeated", "off-topic"] if k in lowered][:4],
        )

    return ScanResult(
        risk_label="SAFE",
        confidence=0.86,
        rationale="No strong moderation risk signal found.",
        highlights=[],
    )


def scan_with_llm(title: str, body: str, provider: str = "auto") -> ScanResult:
    """Use a real LLM if configured, otherwise fall back to deterministic heuristics."""
    provider = (provider or "auto").lower().strip()

    if provider in {"auto", "openai"} and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = f"""Classify the Reddit post into one of:
SAFE, SPAM, PII_LEAK, HARASSMENT, NSFW, OTHER.

Return strict JSON with keys:
risk_label, confidence, rationale, highlights.

Title: {title}
Body: {body}
"""
            resp = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                input=prompt,
            )
            text = getattr(resp, "output_text", "").strip()
            parsed = _parse_llm_json(text)
            return parsed or heuristic_scan(title, body)
        except Exception:
            pass

    if provider in {"auto", "gemini"} and os.getenv("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            prompt = f"""Classify the Reddit post into one of:
SAFE, SPAM, PII_LEAK, HARASSMENT, NSFW, OTHER.

Return strict JSON with keys:
risk_label, confidence, rationale, highlights.

Title: {title}
Body: {body}
"""
            resp = model.generate_content(prompt)
            parsed = _parse_llm_json(getattr(resp, "text", "") or "")
            return parsed or heuristic_scan(title, body)
        except Exception:
            pass

    return heuristic_scan(title, body)


def _parse_llm_json(text: str) -> ScanResult | None:
    import json

    text = text.strip()
    if not text:
        return None

    if text.startswith("```"):
        text = text.strip("`")
    try:
        data = json.loads(text)
        label = str(data.get("risk_label", "OTHER")).upper()
        if label not in {"SAFE", "SPAM", "PII_LEAK", "HARASSMENT", "NSFW", "OTHER"}:
            label = "OTHER"
        return ScanResult(
            risk_label=label,  # type: ignore[arg-type]
            confidence=float(data.get("confidence", 0.5)),
            rationale=str(data.get("rationale", "")),
            highlights=list(data.get("highlights", []) or []),
        )
    except Exception:
        return None
