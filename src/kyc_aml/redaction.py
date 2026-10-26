"""PII redaction for logs and error messages.

The checklist covers CARD NUMBERS and EMAIL ADDRESSES as well as phone
numbers and SSNs. Nothing that looks like PII may reach a log line or an
exception message: callers must pass text through :func:`redact_text`
(or raise via :func:`safe_error`) first.
"""

from __future__ import annotations

import re

_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE = re.compile(
    r"(?:\+\d[\d\s().-]{7,}\d|\(\d{3}\)\s*\d{3}[- ]\d{4}"
    r"|\b\d{3}[- ]\d{3}[- ]\d{4}\b)"
)


def _card_repl(match: "re.Match") -> str:
    digits = re.sub(r"\D", "", match.group(0))
    if 13 <= len(digits) <= 19:
        return "[CARD-REDACTED]"
    return match.group(0)


def redact_text(text: str) -> str:
    """Replace card numbers, emails, SSNs and phone-like strings."""
    if not isinstance(text, str):
        text = str(text)
    text = _CARD.sub(_card_repl, text)
    text = _EMAIL.sub("[EMAIL-REDACTED]", text)
    text = _SSN.sub("[SSN-REDACTED]", text)
    # Phone redaction runs last so it cannot re-expose a redacted card:
    # already-redacted tokens contain no digit runs, so they are safe.
    text = _PHONE.sub("[PHONE-REDACTED]", text)
    return text


def redact_record(record: dict) -> dict:
    """Return a copy of a mapping with every string value redacted."""
    return {k: (redact_text(v) if isinstance(v, str) else v)
            for k, v in record.items()}


def safe_error(message: str) -> ValueError:
    """Build an exception whose message is guaranteed PII-free."""
    return ValueError(redact_text(message))
